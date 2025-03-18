"""
TRAA Python Bindings - Tests

This module contains unit tests for the TRAA library Python bindings.
Tests are organized into separate test classes for each major component:
- Basic data structures (Size, Rect)
- Error handling
- Screen source enumeration
- Screen capture functionality
- Package structure
"""

import unittest
import platform
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

class TestDataStructures(unittest.TestCase):
    """Test basic data structures (Size, Rect)"""
    
    def test_size_creation(self):
        """Test Size class creation and validation"""
        # Test normal creation
        size = Size(1920, 1080)
        self.assertEqual(size.width, 1920)
        self.assertEqual(size.height, 1080)
        
        # Test zero dimensions
        size = Size(0, 0)
        self.assertEqual(size.width, 0)
        self.assertEqual(size.height, 0)
        
        # Test negative dimensions (should raise ValueError)
        with self.assertRaises(ValueError):
            Size(-1, 100)
        with self.assertRaises(ValueError):
            Size(100, -1)
        
        # Test string representation
        size = Size(1920, 1080)
        self.assertEqual(str(size), "1920x1080")
        self.assertEqual(repr(size), "Size(1920, 1080)")
    
    def test_size_conversion(self):
        """Test Size class C structure conversion"""
        # Test normal conversion
        size = Size(1920, 1080)
        c_size = size.to_c_size()
        self.assertEqual(c_size.width, 1920)
        self.assertEqual(c_size.height, 1080)
        
        # Test round-trip conversion
        size2 = Size.from_c_size(c_size)
        self.assertEqual(size2.width, 1920)
        self.assertEqual(size2.height, 1080)
        
        # Test equality after conversion
        self.assertEqual(size, size2)
    
    def test_rect_creation(self):
        """Test Rect class creation and validation"""
        # Test normal creation
        rect = Rect(10, 20, 110, 220)
        self.assertEqual(rect.left, 10)
        self.assertEqual(rect.top, 20)
        self.assertEqual(rect.right, 110)
        self.assertEqual(rect.bottom, 220)
        
        # Test zero-size rect
        rect = Rect(0, 0, 0, 0)
        self.assertEqual(rect.width, 0)
        self.assertEqual(rect.height, 0)
        
        # Test invalid rect (right < left or bottom < top)
        with self.assertRaises(ValueError):
            Rect(100, 20, 50, 220)  # right < left
        with self.assertRaises(ValueError):
            Rect(10, 200, 110, 100)  # bottom < top
        
        # Test string representation
        rect = Rect(10, 20, 110, 220)
        self.assertEqual(str(rect), "(10, 20, 110, 220)")
        self.assertEqual(repr(rect), "Rect(10, 20, 110, 220)")
    
    def test_rect_properties(self):
        """Test Rect class properties"""
        rect = Rect(10, 20, 110, 220)
        
        # Test size properties
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 200)
        
        # Test position properties
        self.assertEqual(rect.x, 10)
        self.assertEqual(rect.y, 20)
        
        # Test center properties
        self.assertEqual(rect.center_x, 60)
        self.assertEqual(rect.center_y, 120)
        
        # Test area property
        self.assertEqual(rect.area, 20000)

class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality"""
    
    def test_error_creation(self):
        """Test Error class creation"""
        # Test with code only
        error = Error(1)
        self.assertEqual(error.code, 1)
        self.assertEqual(error.message, "Unknown error")
        
        # Test with code and message
        error = Error(2, "Custom message")
        self.assertEqual(error.code, 2)
        self.assertEqual(error.message, "Custom message")
        
        # Test string representation
        self.assertEqual(str(error), "TRAA Error 2: Custom message")
        self.assertEqual(repr(error), "Error(2, 'Custom message')")
    
    def test_error_comparison(self):
        """Test Error class comparison"""
        error1 = Error(1, "Message 1")
        error2 = Error(1, "Message 1")
        error3 = Error(2, "Message 2")
        
        # Test equality
        self.assertEqual(error1, error2)
        self.assertNotEqual(error1, error3)
        
        # Test hash
        self.assertEqual(hash(error1), hash(error2))
        self.assertNotEqual(hash(error1), hash(error3))

class TestScreenSourceFlags(unittest.TestCase):
    """Test ScreenSourceFlags enumeration"""
    
    def test_flag_values(self):
        """Test ScreenSourceFlags values"""
        self.assertEqual(ScreenSourceFlags.NONE, 0)
        self.assertEqual(ScreenSourceFlags.IGNORE_SCREEN, 1 << 0)
        self.assertEqual(ScreenSourceFlags.IGNORE_WINDOW, 1 << 1)
        self.assertEqual(ScreenSourceFlags.IGNORE_MINIMIZED, 1 << 2)
    
    def test_flag_operations(self):
        """Test ScreenSourceFlags operations"""
        # Test flag combinations
        flags = ScreenSourceFlags.IGNORE_SCREEN | ScreenSourceFlags.IGNORE_WINDOW
        self.assertEqual(flags, 3)
        
        # Test flag membership
        self.assertTrue(ScreenSourceFlags.IGNORE_SCREEN in flags)
        self.assertTrue(ScreenSourceFlags.IGNORE_WINDOW in flags)
        self.assertFalse(ScreenSourceFlags.IGNORE_MINIMIZED in flags)
        
        # Test flag removal
        flags &= ~ScreenSourceFlags.IGNORE_SCREEN
        self.assertFalse(ScreenSourceFlags.IGNORE_SCREEN in flags)
        self.assertTrue(ScreenSourceFlags.IGNORE_WINDOW in flags)

@pytest.mark.integration
class TestScreenCapture(unittest.TestCase):
    """Test screen capture functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.sources = traa.enum_screen_sources()
        if not self.sources:
            self.skipTest("No screen sources available")
    
    def test_enum_screen_sources_basic(self):
        """Test basic screen source enumeration"""
        # Test without thumbnails
        sources = traa.enum_screen_sources()
        self.assertIsInstance(sources, list)
        
        if sources:
            source = sources[0]
            self.assertIsInstance(source, ScreenSourceInfo)
            self.assertIsInstance(source.id, int)
            self.assertIsInstance(source.is_window, bool)
            self.assertIsInstance(source.rect, Rect)
            self.assertIsInstance(source.title, str)
            
            # Verify no thumbnails when not requested
            self.assertIsNone(source.icon_data)
            self.assertIsNone(source.thumbnail_data)
    
    def test_enum_screen_sources_with_images(self):
        """Test screen source enumeration with thumbnails"""
        sources = traa.enum_screen_sources(
            icon_size=Size(16, 16),
            thumbnail_size=Size(160, 120)
        )
        
        if sources:
            source = sources[0]
            if source.icon_data is not None:
                self.assertIsInstance(source.icon_data, np.ndarray)
                self.assertEqual(source.icon_data.shape[:2], (16, 16))
            
            if source.thumbnail_data is not None:
                self.assertIsInstance(source.thumbnail_data, np.ndarray)
                # Check that thumbnail dimensions are reasonable
                height, width = source.thumbnail_data.shape[:2]
                # Allow some flexibility in dimensions to account for aspect ratio preservation
                self.assertLessEqual(height, 120 * 1.5)  # Height should not exceed 150% of requested height
                self.assertLessEqual(width, 160 * 1.5)   # Width should not exceed 150% of requested width
                self.assertGreater(height, 0)            # Height should be positive
                self.assertGreater(width, 0)             # Width should be positive
                # Check aspect ratio is preserved within reasonable bounds
                original_ratio = 160 / 120
                actual_ratio = width / height
                self.assertAlmostEqual(original_ratio, actual_ratio, delta=0.5)
    
    def test_enum_screen_sources_with_flags(self):
        """Test screen source enumeration with flags"""
        # Test IGNORE_WINDOW flag
        sources = traa.enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_WINDOW
        )
        self.assertTrue(all(not source.is_window for source in sources))
        
        # Test IGNORE_SCREEN flag
        sources = traa.enum_screen_sources(
            external_flags=ScreenSourceFlags.IGNORE_SCREEN
        )
        self.assertTrue(all(source.is_window for source in sources))
    
    def test_create_snapshot_basic(self):
        """Test basic snapshot creation"""
        if not self.sources:
            self.skipTest("No screen sources available")
        
        source = self.sources[0]
        size = Size(800, 600)
        
        # Create snapshot
        image, actual_size = traa.create_snapshot(source.id, size)
        
        # Verify result
        self.assertIsInstance(image, np.ndarray)
        self.assertIsInstance(actual_size, Size)
        
        # Check image dimensions
        self.assertEqual(image.shape[0], actual_size.height)
        self.assertEqual(image.shape[1], actual_size.width)
        
        # Check image format
        self.assertIn(len(image.shape), [2, 3])
        if len(image.shape) == 3:
            self.assertIn(image.shape[2], [3, 4])
    
    def test_create_snapshot_sizes(self):
        """Test snapshot creation with different sizes"""
        if not self.sources:
            self.skipTest("No screen sources available")
        
        source = self.sources[0]
        
        # Test different sizes
        sizes = [
            Size(320, 240),
            Size(640, 480),
            Size(1280, 720),
            Size(1920, 1080)
        ]
        
        for size in sizes:
            image, actual_size = traa.create_snapshot(source.id, size)
            self.assertIsInstance(image, np.ndarray)
            self.assertGreater(actual_size.width, 0)
            self.assertGreater(actual_size.height, 0)
    
    def test_create_snapshot_errors(self):
        """Test snapshot creation error handling"""
        # Test invalid source ID
        with self.assertRaises(Error):
            traa.create_snapshot(99999, Size(800, 600))
        
        # Test invalid size
        if self.sources:
            source = self.sources[0]
            with self.assertRaises(ValueError):
                traa.create_snapshot(source.id, Size(0, 0))
            with self.assertRaises(ValueError):
                traa.create_snapshot(source.id, Size(-1, -1))

class TestPackageStructure(unittest.TestCase):
    """Test package structure and exports"""
    
    def test_package_exports(self):
        """Test package exports"""
        # Check required attributes
        required_attrs = [
            'Error',
            'Size',
            'Rect',
            'ScreenSourceInfo',
            'ScreenSourceFlags',
            'create_snapshot',
            'enum_screen_sources',
            '__version__'
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(traa, attr), f"Missing attribute: {attr}")
        
        # Check private attributes are not exported
        # private_attrs = ['TRAA', '_TRAA']  # 'traa' is the module itself
        # for attr in private_attrs:
        #     self.assertFalse(hasattr(traa, attr), f"Private attribute exposed: {attr}")
    
    def test_version_format(self):
        """Test version string format"""
        version = traa.__version__
        self.assertIsInstance(version, str)
        self.assertRegex(version, r'^\d+\.\d+\.\d+')

if __name__ == '__main__':
    unittest.main()