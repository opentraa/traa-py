#!/usr/bin/env python3
"""
TRAA Screen Source Enumeration Example

This example demonstrates how to enumerate and filter screen sources using the TRAA library.
It shows how to:
1. Use different ScreenSourceFlags to filter sources
2. Get thumbnails and icons for sources
3. Display detailed information about each source
"""

import os
import sys
from PIL import Image

# Add parent directory to path to import traa package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traa import (
    Size,
    ScreenSourceFlags,
    ScreenSourceInfo,
    enum_screen_sources,
)

def print_sources(sources, title):
    """Print information about screen sources"""
    print(f"\n{title} ({len(sources)} sources):")
    for i, source in enumerate(sources):
        print(f"{i + 1}. {source}")
        print(f"   ID: {source.id}")
        print(f"   Type: {'Window' if source.is_window else 'Display'}")
        print(f"   Title: {source.title}")
        print(f"   Rect: {source.rect}")
        if source.is_window:
            print(f"   Process Path: {source.process_path}")
            print(f"   Is Minimized: {source.is_minimized}")
        else:
            print(f"   Is Primary: {source.is_primary}")
        
        # Save thumbnail if available
        if source.thumbnail_data is not None:
            thumb_path = f"thumb_{title.lower().replace(' ', '_')}_{i + 1}.png"
            Image.fromarray(source.thumbnail_data).save(thumb_path)
            print(f"   Thumbnail saved to: {thumb_path}")
        
        # Save icon if available
        if source.icon_data is not None:
            icon_path = f"icon_{title.lower().replace(' ', '_')}_{i + 1}.png"
            Image.fromarray(source.icon_data).save(icon_path)
            print(f"   Icon saved to: {icon_path}")

def main():
    """Main function"""
    try:
        # Get all sources with thumbnails and icons
        print("Enumerating all screen sources...")
        all_sources = enum_screen_sources(
            thumbnail_size=Size(160, 120),
            icon_size=Size(32, 32)
        )
        print_sources(all_sources, "All Sources")
        
        # Get only displays (no windows)
        print("\nEnumerating displays only...")
        displays = enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_WINDOW
        )
        print_sources(displays, "Displays Only")
        
        # Get only windows (no displays)
        print("\nEnumerating windows only...")
        windows = enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_SCREEN
        )
        print_sources(windows, "Windows Only")
        
        # Get non-minimized windows only
        print("\nEnumerating non-minimized windows...")
        active_windows = enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_SCREEN | 
                         ScreenSourceFlags.IGNORE_MINIMIZED
        )
        print_sources(active_windows, "Non-minimized Windows")
        
        # Get all sources including system windows and tool windows
        print("\nEnumerating all sources including system and tool windows...")
        all_with_system = enum_screen_sources(
            external_flags=ScreenSourceFlags.NOT_SKIP_SYSTEM_WINDOWS | 
                         ScreenSourceFlags.NOT_IGNORE_TOOLWINDOW
        )
        print_sources(all_with_system, "All Sources Including System Windows")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 