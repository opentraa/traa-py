"""
TRAA Python API

This module provides a Python friendly interface to the TRAA C library.
"""

import os
import sys
import platform
import threading
import atexit
from typing import List, Tuple, Callable, Optional, Union, Dict, Any
import numpy as np
from enum import IntFlag

from ._traa_cffi import ffi, _lib

# Error code mapping
class Error(Exception):
    """TRAA library error exception"""
    def __init__(self, code: int, message: str = None):
        self.code = code
        self.message = message or self._get_error_message(code)
        super().__init__(f"TRAA Error {code}: {self.message}")
    
    @staticmethod
    def _get_error_message(code: int) -> str:
        """Get error message for error code"""
        if code == 0:
            return "Success"
        
        # Use predefined error messages
        error_messages = {
            0: "Success",
            1: "Unknown error",
            2: "Invalid argument",
            3: "Invalid state",
            4: "Not implemented",
            5: "Not supported",
            6: "Out of memory",
            7: "Out of range",
            8: "Permission denied",
            9: "Resource busy",
            10: "Resource exhausted",
            11: "Resource unavailable",
            12: "Timed out",
            13: "Too many requests",
            14: "Unavailable",
            15: "Unauthorized",
            16: "Unsupported media type",
            17: "Already exists",
            18: "Not found",
            19: "Not initialized",
            20: "Already initialized",
            21: "Enumerate screen source info failed",
            22: "Invalid source ID"
        }
        
        return error_messages.get(code, f"Unknown error code: {code}")

# Decorator to check error codes
def check_error(func):
    """Check TRAA function return value, throw exception if not success"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, int) and result != 0:
            raise Error(result)
        return result
    return wrapper

# Size class
class Size:
    """Class representing width and height"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def to_c_size(self):
        """Convert to C structure"""
        c_size = ffi.new("traa_size*")
        c_size.width = self.width
        c_size.height = self.height
        return c_size
    
    @classmethod
    def from_c_size(cls, c_size):
        """Create Size object from C structure"""
        return cls(c_size.width, c_size.height)
    
    def __str__(self) -> str:
        return f"{self.width}x{self.height}"
    
    def __repr__(self) -> str:
        return f"Size({self.width}, {self.height})"

# Rect class
class Rect:
    """Class representing a rectangle with left, top, right, bottom coordinates"""
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
    
    def to_c_rect(self):
        """Convert to C structure"""
        c_rect = ffi.new("traa_rect*")
        c_rect.left = self.left
        c_rect.top = self.top
        c_rect.right = self.right
        c_rect.bottom = self.bottom
        return c_rect
    
    @classmethod
    def from_c_rect(cls, c_rect):
        """Create Rect object from C structure"""
        return cls(c_rect.left, c_rect.top, c_rect.right, c_rect.bottom)
    
    @property
    def width(self) -> int:
        """Get width of rectangle"""
        return self.right - self.left
    
    @property
    def height(self) -> int:
        """Get height of rectangle"""
        return self.bottom - self.top
    
    def __str__(self) -> str:
        return f"({self.left}, {self.top}, {self.right}, {self.bottom})"
    
    def __repr__(self) -> str:
        return f"Rect({self.left}, {self.top}, {self.right}, {self.bottom})"

# ScreenSourceInfo class
class ScreenSourceInfo:
    """Class representing information about a screen source (display or window)"""
    def __init__(self, c_info):
        """
        Initialize from C structure
        
        Args:
            c_info: C structure containing screen source information
        """
        self.id = c_info.id
        self.screen_id = c_info.screen_id
        self.is_window = bool(c_info.is_window)
        self.is_minimized = bool(c_info.is_minimized)
        self.is_maximized = bool(c_info.is_maximized)
        self.is_primary = bool(c_info.is_primary)
        self.rect = Rect.from_c_rect(c_info.rect)
        self.icon_size = Size.from_c_size(c_info.icon_size)
        self.thumbnail_size = Size.from_c_size(c_info.thumbnail_size)
        self.title = ffi.string(c_info.title).decode('utf-8', errors='replace') if c_info.title != ffi.NULL else ""
        self.process_path = ffi.string(c_info.process_path).decode('utf-8', errors='replace') if c_info.process_path != ffi.NULL else ""
        
        # Handle icon data if available
        self.icon_data = None
        if c_info.icon_data != ffi.NULL and self.icon_size.width > 0 and self.icon_size.height > 0:
            icon_size_bytes = self.icon_size.width * self.icon_size.height * 4  # Assuming RGBA
            buffer = ffi.buffer(c_info.icon_data, icon_size_bytes)
            icon_data = np.frombuffer(buffer, dtype=np.uint8).copy()
            self.icon_data = icon_data.reshape((self.icon_size.height, self.icon_size.width, 4))
        
        # Handle thumbnail data if available
        self.thumbnail_data = None
        if c_info.thumbnail_data != ffi.NULL and self.thumbnail_size.width > 0 and self.thumbnail_size.height > 0:
            thumbnail_size_bytes = self.thumbnail_size.width * self.thumbnail_size.height * 4  # Assuming RGBA
            buffer = ffi.buffer(c_info.thumbnail_data, thumbnail_size_bytes)
            thumbnail_data = np.frombuffer(buffer, dtype=np.uint8).copy()
            self.thumbnail_data = thumbnail_data.reshape((self.thumbnail_size.height, self.thumbnail_size.width, 4))
    
    def __str__(self) -> str:
        if self.is_window:
            return f"Window: {self.title} (ID: {self.id}) ({self.rect})"
        else:
            return f"Display: (ID: {self.id}){' (Primary)' if self.is_primary else ''} ({self.rect})"
    
    def __repr__(self) -> str:
        return f"ScreenSourceInfo(id={self.id}, title='{self.title}', is_window={self.is_window})"

# Screen source enumeration flags
class ScreenSourceFlags(IntFlag):
    """Flags controlling screen source enumeration behavior"""
    NONE = 0
    IGNORE_SCREEN = 1 << 0
    IGNORE_WINDOW = 1 << 1
    IGNORE_MINIMIZED = 1 << 2
    NOT_IGNORE_UNTITLED = 1 << 3
    NOT_IGNORE_UNRESPONSIVE = 1 << 4
    IGNORE_CURRENT_PROCESS_WINDOWS = 1 << 5
    NOT_IGNORE_TOOLWINDOW = 1 << 6
    IGNORE_NOPROCESS_PATH = 1 << 7
    NOT_SKIP_SYSTEM_WINDOWS = 1 << 8
    NOT_SKIP_ZERO_LAYER_WINDOWS = 1 << 9
    ALL = 0xFFFFFFFF

# TRAA library main class
class _TRAA:
    """TRAA library main class"""
    _instance = None
    _lock = threading.Lock()
    _initialized = True  # Assume library is initialized when loaded
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(_TRAA, cls).__new__(cls)
            return cls._instance
    
    @classmethod
    @check_error
    def enum_screen_sources(cls, icon_size: Size = None, thumbnail_size: Size = None, external_flags: Union[int, ScreenSourceFlags] = ScreenSourceFlags.NONE) -> List[ScreenSourceInfo]:
        """
        Enumerate available screen sources (displays and windows)
        
        Args:
            icon_size: Size for icons, None for no icons
            thumbnail_size: Size for thumbnails, None for no thumbnails
            external_flags: Flags to control enumeration behavior. Can be combination of ScreenSourceFlags:
                ScreenSourceFlags.NONE - Default behavior
                ScreenSourceFlags.IGNORE_SCREEN - Ignore display screens
                ScreenSourceFlags.IGNORE_WINDOW - Ignore windows
                ScreenSourceFlags.IGNORE_MINIMIZED - Ignore minimized windows
                ScreenSourceFlags.NOT_IGNORE_UNTITLED - Include untitled windows
                ScreenSourceFlags.NOT_IGNORE_UNRESPONSIVE - Include unresponsive windows
                ScreenSourceFlags.IGNORE_CURRENT_PROCESS_WINDOWS - Ignore windows from current process
                ScreenSourceFlags.NOT_IGNORE_TOOLWINDOW - Include tool windows
                ScreenSourceFlags.IGNORE_NOPROCESS_PATH - Ignore windows without process path
                ScreenSourceFlags.NOT_SKIP_SYSTEM_WINDOWS - Include system windows
                ScreenSourceFlags.NOT_SKIP_ZERO_LAYER_WINDOWS - Include zero layer windows
                ScreenSourceFlags.ALL - All flags enabled
                
                Flags can be combined using bitwise OR operator (|)
                Example: ScreenSourceFlags.IGNORE_SCREEN | ScreenSourceFlags.IGNORE_MINIMIZED
            
        Returns:
            List[ScreenSourceInfo]: List of available screen sources
        """
        # Create default sizes if not provided
        if icon_size is None:
            icon_size = Size(0, 0)
        if thumbnail_size is None:
            thumbnail_size = Size(0, 0)
        
        # Create C structures
        c_icon_size = icon_size.to_c_size()
        c_thumbnail_size = thumbnail_size.to_c_size()
        c_infos_ptr = ffi.new("traa_screen_source_info**")
        c_count = ffi.new("int*")
        
        # Call C function
        error_code = _lib.traa_enum_screen_source_info(
            c_icon_size[0],  # Pass structure instead of pointer
            c_thumbnail_size[0],
            external_flags,
            c_infos_ptr,
            c_count
        )
        
        if error_code != 0:
            raise Error(error_code)
        
        # Get result
        count = c_count[0]
        infos_ptr = c_infos_ptr[0]
        
        # Convert C data to Python objects
        result = []
        for i in range(count):
            info = ScreenSourceInfo(infos_ptr[i])
            result.append(info)
        
        # Free C memory
        _lib.traa_free_screen_source_info(infos_ptr, count)
        
        return result
    
    @classmethod
    @check_error
    def create_snapshot(cls, source_id: int, snapshot_size: Size) -> Tuple[np.ndarray, Size]:
        """
        Create snapshot
        
        Args:
            source_id: Source ID
            snapshot_size: Requested snapshot size
            
        Returns:
            Tuple[np.ndarray, Size]: Snapshot data and actual size
        """
        # Create C structure
        c_size = snapshot_size.to_c_size()
        c_actual_size = ffi.new("traa_size*")
        c_data_ptr = ffi.new("uint8_t**")
        c_data_size = ffi.new("int*")
        
        # Call C function
        error_code = _lib.traa_create_snapshot(
            source_id, 
            c_size[0],  # Pass structure instead of pointer
            c_data_ptr, 
            c_data_size, 
            c_actual_size
        )
        
        if error_code != 0:
            raise Error(error_code)
        
        # Get result
        data_size = c_data_size[0]
        data_ptr = c_data_ptr[0]
        
        # Convert C data to numpy array
        buffer = ffi.buffer(data_ptr, data_size)
        data = np.frombuffer(buffer, dtype=np.uint8).copy()
        
        # Free C memory
        _lib.traa_free_snapshot(data_ptr)
        
        # Get actual size
        actual_size = Size.from_c_size(c_actual_size[0])
        
        # Reshape array to image shape
        if len(data) == actual_size.width * actual_size.height * 3:  # RGB
            data = data.reshape((actual_size.height, actual_size.width, 3))
        elif len(data) == actual_size.width * actual_size.height * 4:  # RGBA
            data = data.reshape((actual_size.height, actual_size.width, 4))
        elif len(data) == actual_size.width * actual_size.height:  # Grayscale
            data = data.reshape((actual_size.height, actual_size.width))
        
        return data, actual_size 