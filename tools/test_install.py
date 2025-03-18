#!/usr/bin/env python3
"""
TRAA Installation Test Script

This script verifies the installation of the TRAA library by:
1. Checking if the package can be imported
2. Verifying the presence of native libraries
3. Testing basic functionality
"""

import os
import sys
import platform
from pathlib import Path

def print_section(title):
    """Print a section title"""
    print(f"\n{'='*20} {title} {'='*20}")

def check_import():
    """Test if the package can be imported"""
    print_section("Testing Import")
    try:
        import traa
        print("✓ Successfully imported traa")
        print(f"Version: {traa.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import traa: {e}")
        return False

def check_library_files():
    """Check if the native library files are present"""
    print_section("Checking Library Files")
    
    try:
        import traa
        package_path = os.path.dirname(traa.__file__)
        libs_path = os.path.join(package_path, 'libs')
        
        if not os.path.exists(libs_path):
            print(f"✗ Libs directory not found at: {libs_path}")
            return False
        
        # Check platform-specific libraries
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == 'darwin':
            # Check for macOS dynamic library
            lib_path = os.path.join(libs_path, 'darwin', 'libtraa.dylib')
            if not os.path.exists(lib_path):
                print(f"✗ Dynamic library not found at: {lib_path}")
                return False
            print(f"✓ Found dynamic library at: {lib_path}")
            
        elif system == 'windows':
            # Check for Windows DLL based on architecture
            if machine in ['amd64', 'x86_64', 'arm64']:
                arch_path = 'x64'
            elif machine == 'x86':
                arch_path = 'x86'
            else:
                print(f"✗ Unsupported Windows architecture: {machine}")
                return False
                
            dll_path = os.path.join(libs_path, 'windows', arch_path, 'traa.dll')
            if not os.path.exists(dll_path):
                print(f"✗ DLL not found at: {dll_path}")
                return False
            print(f"✓ Found DLL at: {dll_path}")
            
        elif system == 'linux':
            # Check for Linux shared library based on architecture
            if machine in ['x86_64', 'amd64']:
                arch_path = 'x64'
            elif machine in ['aarch64', 'arm64']:
                arch_path = 'arm64'
            else:
                print(f"✗ Unsupported Linux architecture: {machine}")
                return False
                
            so_path = os.path.join(libs_path, 'linux', arch_path, 'libtraa.so')
            if not os.path.exists(so_path):
                print(f"✗ Shared library not found at: {so_path}")
                return False
            print(f"✓ Found shared library at: {so_path}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error checking library files: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of the library"""
    print_section("Testing Basic Functionality")
    try:
        from traa import Size, ScreenSourceFlags, enum_screen_sources
        
        # Try to enumerate screen sources
        sources = enum_screen_sources(
            thumbnail_size=Size(160, 120),
            external_flags=ScreenSourceFlags.NONE
        )
        
        print(f"✓ Successfully enumerated {len(sources)} screen sources")
        
        # Print first source info
        if sources:
            source = sources[0]
            print(f"\nFirst source details:")
            print(f"  ID: {source.id}")
            print(f"  Type: {'Window' if source.is_window else 'Display'}")
            print(f"  Title: {source.title}")
            print(f"  Rectangle: {source.rect}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing functionality: {e}")
        return False

def main():
    """Main test function"""
    success = True
    
    # Run tests
    if not check_import():
        success = False
    
    if not check_library_files():
        success = False
    
    if not test_basic_functionality():
        success = False
    
    # Print final result
    print_section("Test Results")
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 