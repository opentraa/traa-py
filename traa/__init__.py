"""
TRAA Python Package

This package provides a Python interface to the TRAA C library for screen capture
and image processing functionality.
"""

from .traa import (
    Error,
    Size,
    Rect,
    ScreenSourceInfo,
    ScreenSourceFlags,
    _TRAA,
)

# Create a singleton instance for easy access
_traa = _TRAA()

# Export the functions at the package level for convenience
create_snapshot = _traa.create_snapshot
enum_screen_sources = _traa.enum_screen_sources

# Version information
__version__ = "0.1.0"  # Update with actual version

# Export all public symbols
__all__ = [
    "Error",
    "Size",
    "Rect",
    "ScreenSourceFlags",
    "ScreenSourceInfo",
    "create_snapshot",
    "enum_screen_sources",
]
