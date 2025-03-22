#!/usr/bin/env python3
"""
TRAA Basic Usage Example

This example demonstrates basic usage of the TRAA library for screen capture.
It shows how to:
1. Enumerate available screen sources (displays and windows)
2. Create a snapshot from a selected source
3. Save the snapshot as a PNG file
"""

import os
import sys
from PIL import Image

# Add parent directory to path to import traa package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traa import (
    Size,
    ScreenSourceFlags,
    create_snapshot,
    enum_screen_sources,
)

def ensure_tmp_dir():
    """Create tmp directory if it doesn't exist"""
    tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir

def main():
    """Main function"""
    try:
        # Enumerate screen sources with thumbnails
        print("Enumerating screen sources...")
        sources = enum_screen_sources(
            external_flags=ScreenSourceFlags.NONE
        )
        
        if not sources:
            print("No screen sources found!")
            return 1
        
        # Print available sources
        print("\nAvailable sources:")
        for i, source in enumerate(sources):
            print(f"{i + 1}. {source}")
        
        # Let user select a source
        while True:
            try:
                choice = int(input("\nSelect a source (1-{0}): ".format(len(sources))))
                if 1 <= choice <= len(sources):
                    break
                print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
        
        # Get selected source
        source = sources[choice - 1]
        print(f"\nSelected source: {source}")
        
        # Create snapshot
        print("\nCreating snapshot...")
        image, actual_size = create_snapshot(source.id, Size(1920, 1080))
        
        if image is None:
            print("Failed to create snapshot!")
            return 1
        
        # Determine image mode based on shape
        if len(image.shape) == 3 and image.shape[2] == 3:
            mode = "RGB"
        elif len(image.shape) == 3 and image.shape[2] == 4:
            mode = "RGBA"
        else:
            mode = "L"  # Grayscale
        
        # Save snapshot
        tmp_dir = ensure_tmp_dir()
        output_path = os.path.join(tmp_dir, "snapshot.png")
        Image.fromarray(image, mode=mode).save(output_path)
        print(f"Snapshot saved to: {output_path}")
        print(f"Image size: {actual_size}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 