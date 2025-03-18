import os
import sys
import platform
from pathlib import Path
import cffi

ffi = cffi.FFI()

try:
    ffi.cdef("""
typedef struct traa_size {
  int32_t width;
  int32_t height;
} traa_size;
             
typedef struct traa_rect {
  int32_t left;
  int32_t top;
  int32_t right;
  int32_t bottom;
} traa_rect;
             
typedef struct traa_screen_source_info {
  int64_t id;
  int64_t screen_id;
  bool is_window;
  bool is_minimized;
  bool is_maximized;
  bool is_primary;
  traa_rect rect;
  traa_size icon_size;
  traa_size thumbnail_size;
  const char title[256];
  const char process_path[256];
  const uint8_t *icon_data;
  const uint8_t *thumbnail_data;
} traa_screen_source_info;
             
int traa_enum_screen_source_info(const traa_size icon_size, const traa_size thumbnail_size, const unsigned int external_flags, traa_screen_source_info **infos, int *count);
             
int traa_free_screen_source_info(traa_screen_source_info infos[], int count);             
             
int traa_create_snapshot(const int64_t source_id, const traa_size snapshot_size, uint8_t **data, int *data_size, traa_size *actual_size);             
             
void traa_free_snapshot(uint8_t *data);
    """)
    
    def get_lib_path():
        """Get library file path"""
        # Get current module directory
        base_path = Path(__file__).parent.absolute()
        
        # Select correct library file name and path based on platform
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == 'windows':
            lib_name = 'traa.dll'
            if machine in ['amd64', 'x86_64', 'arm64']:
                lib_path = base_path / "libs" / "windows" / "x64" / lib_name
            elif machine == 'x86':
                lib_path = base_path / "libs" / "windows" / "x86" / lib_name
            else:
                raise RuntimeError(f"Unsupported Windows architecture: {machine}")
        elif system == 'darwin':  # macOS
            lib_name = 'libtraa.dylib'
            lib_path = base_path / "libs" / "darwin" / lib_name
        elif system == 'linux':
            lib_name = 'libtraa.so'
            if machine in ['x86_64', 'amd64']:
                lib_path = base_path / "libs" / "linux" / "x64" / lib_name
            elif machine in ['aarch64', 'arm64']:
                lib_path = base_path / "libs" / "linux" / "arm64" / lib_name
            else:
                raise RuntimeError(f"Unsupported Linux architecture: {machine}")
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        if lib_path.exists():
            return str(lib_path)
        
        raise FileNotFoundError(f"Could not find {lib_name} library in {lib_path}")
    
    # Load library
    _lib = ffi.dlopen(get_lib_path())
    
except Exception as e:
    print(f"Warning: Failed to load TRAA library: {e}")
    _lib = None

# Check if library is loaded successfully
if _lib is None:
    raise ImportError("Failed to load TRAA library") 