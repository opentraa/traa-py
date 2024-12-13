"""
TRAA Python Bindings - Tests
"""

import unittest
import numpy as np
import pytest

# Try to import traa package
try:
    import traa
    from traa import Error, Size, Rect, ScreenSourceInfo, ScreenSourceFlags
    TRAA_AVAILABLE = True
except ImportError:
    TRAA_AVAILABLE = False

# Skip all tests if library is not available
pytestmark = pytest.mark.skipif(not TRAA_AVAILABLE, reason="TRAA library not available")

class TestTraa(unittest.TestCase):
    """TRAA library test class"""
    
    def test_size(self):
        """Test Size class"""
        # Create size
        size = Size(1920, 1080)
        self.assertEqual(size.width, 1920)
        self.assertEqual(size.height, 1080)
        
        # Test string representation
        self.assertEqual(str(size), "1920x1080")
        self.assertEqual(repr(size), "Size(1920, 1080)")
        
        # Test C structure conversion
        c_size = size.to_c_size()
        self.assertEqual(c_size.width, 1920)
        self.assertEqual(c_size.height, 1080)
        
        # Test from_c_size class method
        size2 = Size.from_c_size(c_size)
        self.assertEqual(size2.width, 1920)
        self.assertEqual(size2.height, 1080)
    
    def test_rect(self):
        """Test Rect class"""
        # Create rect
        rect = Rect(10, 20, 110, 220)
        self.assertEqual(rect.left, 10)
        self.assertEqual(rect.top, 20)
        self.assertEqual(rect.right, 110)
        self.assertEqual(rect.bottom, 220)
        
        # Test width and height properties
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 200)
        
        # Test string representation
        self.assertEqual(str(rect), "(10, 20, 110, 220)")
        self.assertEqual(repr(rect), "Rect(10, 20, 110, 220)")
        
        # Test C structure conversion
        c_rect = rect.to_c_rect()
        self.assertEqual(c_rect.left, 10)
        self.assertEqual(c_rect.top, 20)
        self.assertEqual(c_rect.right, 110)
        self.assertEqual(c_rect.bottom, 220)
        
        # Test from_c_rect class method
        rect2 = Rect.from_c_rect(c_rect)
        self.assertEqual(rect2.left, 10)
        self.assertEqual(rect2.top, 20)
        self.assertEqual(rect2.right, 110)
        self.assertEqual(rect2.bottom, 220)
    
    def test_error(self):
        """Test error handling"""
        # Test error creation
        error = Error(1)
        self.assertEqual(error.code, 1)
        self.assertEqual(error.message, "Unknown error")
        
        # Test custom message
        error = Error(2, "Custom message")
        self.assertEqual(error.code, 2)
        self.assertEqual(error.message, "Custom message")
        
        # Test string representation
        self.assertEqual(str(error), "TRAA Error 2: Custom message")
    
    def test_screen_source_flags(self):
        """Test ScreenSourceFlags enum"""
        # Test individual flags
        self.assertEqual(ScreenSourceFlags.NONE, 0)
        self.assertEqual(ScreenSourceFlags.IGNORE_SCREEN, 1 << 0)
        self.assertEqual(ScreenSourceFlags.IGNORE_WINDOW, 1 << 1)
        
        # Test flag combinations
        combined = ScreenSourceFlags.IGNORE_SCREEN | ScreenSourceFlags.IGNORE_WINDOW
        self.assertEqual(combined, 3)
        
        # Test flag membership
        self.assertTrue(ScreenSourceFlags.IGNORE_SCREEN in combined)
        self.assertTrue(ScreenSourceFlags.IGNORE_WINDOW in combined)
        self.assertFalse(ScreenSourceFlags.IGNORE_MINIMIZED in combined)
    
    @pytest.mark.xfail(reason="Requires actual screen source")
    def test_enum_screen_sources(self):
        """Test enum_screen_sources function"""
        # Enumerate screen sources without thumbnails or icons
        sources = traa.enum_screen_sources()
        
        # Verify result
        self.assertIsInstance(sources, list)
        
        # If sources are found, check their properties
        if sources:
            source = sources[0]
            self.assertIsInstance(source, ScreenSourceInfo)
            self.assertIsInstance(source.id, int)
            self.assertIsInstance(source.is_window, bool)
            self.assertIsInstance(source.rect, Rect)
            self.assertIsInstance(source.title, str)
            
            # Test string representation
            self.assertIsInstance(str(source), str)
            self.assertIsInstance(repr(source), str)
            
            # Verify icon and thumbnail are None (since we didn't request them)
            self.assertIsNone(source.icon_data)
            self.assertIsNone(source.thumbnail_data)
        
        # Test with icon and thumbnail sizes
        sources_with_images = traa.enum_screen_sources(
            icon_size=Size(16, 16),
            thumbnail_size=Size(160, 120)
        )
        
        # Test with flags
        sources_no_windows = traa.enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_WINDOW
        )
        
        # Verify no windows in result
        self.assertTrue(all(not source.is_window for source in sources_no_windows))
        
        # Test combining flags
        sources_filtered = traa.enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_WINDOW | ScreenSourceFlags.IGNORE_MINIMIZED
        )
        
        # Verify result
        self.assertIsInstance(sources_filtered, list)
    
    @pytest.mark.xfail(reason="Requires actual screen source")
    def test_create_snapshot(self):
        """Test create_snapshot function"""
        # Create size
        size = Size(800, 600)
        
        # Create snapshot
        # Using source_id=0 which is typically the primary display
        image, actual_size = traa.create_snapshot(0, size)
        
        # Verify result
        self.assertIsInstance(image, np.ndarray)
        self.assertIsInstance(actual_size, Size)
        
        # Check if image has correct dimensions
        # The actual size might differ from requested size depending on implementation
        self.assertEqual(image.shape[0], actual_size.height)
        self.assertEqual(image.shape[1], actual_size.width)
        
        # Check if image has correct number of channels (RGB or RGBA)
        self.assertIn(len(image.shape), [2, 3])  # Either grayscale or color
        if len(image.shape) == 3:
            self.assertIn(image.shape[2], [3, 4])  # Either RGB or RGBA
    
    @pytest.mark.xfail(reason="Requires actual screen source")
    def test_capture_from_enum(self):
        """Test capturing from enumerated sources"""
        # Enumerate screen sources
        sources = traa.enum_screen_sources()
        
        # Skip test if no sources found
        if not sources:
            pytest.skip("No screen sources found")
        
        # Try to capture from the first source
        source = sources[0]
        image, actual_size = traa.create_snapshot(source.id, Size(640, 480))
        
        # Verify result
        self.assertIsInstance(image, np.ndarray)
        self.assertIsInstance(actual_size, Size)
        
        # Check if image has correct dimensions
        self.assertEqual(image.shape[0], actual_size.height)
        self.assertEqual(image.shape[1], actual_size.width)
    
    @pytest.mark.xfail(reason="Requires actual screen source")
    def test_error_handling(self):
        """Test error handling with invalid parameters"""
        # Try to create snapshot with invalid source_id
        with self.assertRaises(Error):
            # Using a very large source_id that is unlikely to exist
            traa.create_snapshot(99999, Size(800, 600))
    
    def test_package_exports(self):
        """Test package exports"""
        # Check if all expected symbols are exported
        self.assertTrue(hasattr(traa, 'Error'))
        self.assertTrue(hasattr(traa, 'Size'))
        self.assertTrue(hasattr(traa, 'Rect'))
        self.assertTrue(hasattr(traa, 'ScreenSourceInfo'))
        self.assertTrue(hasattr(traa, 'ScreenSourceFlags'))
        self.assertTrue(hasattr(traa, 'create_snapshot'))
        self.assertTrue(hasattr(traa, 'enum_screen_sources'))
        self.assertTrue(hasattr(traa, '__version__'))
        
        # Verify TRAA class is not exported
        self.assertFalse(hasattr(traa, 'TRAA'))
        self.assertFalse(hasattr(traa, '_TRAA'))
        self.assertFalse(hasattr(traa, 'traa'))

if __name__ == '__main__':
    unittest.main()