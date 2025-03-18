#!/usr/bin/env python3
"""
Build script for creating wheels for all supported platforms
"""

import os
import shutil
import subprocess
import sys
import glob

# Supported platforms
PLATFORMS = [
    'windows_x64',
    'windows_x86',
    'windows_arm64',
    'darwin_x64',
    'darwin_arm64',
    'linux_x64',
    'linux_arm64'
]

def clean_build_dirs():
    """Clean up build directories"""
    dirs_to_clean = ['build', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in glob.glob(dir_pattern):
            shutil.rmtree(path, ignore_errors=True)
    print("Cleaned build directories")

def build_wheel(platform):
    """Build wheel for specified platform"""
    print(f"\nBuilding wheel for {platform}")
    
    # Set environment variable for target platform
    env = os.environ.copy()
    env['TARGET_PLATFORM'] = platform
    
    # Clean previous build artifacts (except dist directory)
    clean_build_dirs()
    
    # Build wheel
    try:
        subprocess.check_call([sys.executable, "setup.py", "bdist_wheel"], env=env)
        print(f"Successfully built wheel for {platform}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build wheel for {platform}: {e}")
        return False

def main():
    """Main build function"""
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Build wheels for all platforms
    success = True
    for platform in PLATFORMS:
        if not build_wheel(platform):
            success = False
    
    if success:
        print("\nAll wheels built successfully!")
        print("Wheels can be found in the 'dist' directory:")
        for wheel in glob.glob("dist/*.whl"):
            print(f"  - {os.path.basename(wheel)}")
    else:
        print("\nSome wheels failed to build. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 