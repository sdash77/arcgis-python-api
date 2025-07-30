import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from arcgis.features.geo._io.fileops import _ensure_path_string

class TestGeoIoFileOps(unittest.TestCase):
    
    def test_ensure_path_string_input_is_string(self):
        input_path = "/path/to/file.shp"
        result = _ensure_path_string(input_path)
        self.assertEqual(result, input_path)

    def test_ensure_path_string_input_is_path_object(self):
        input_path = Path("/path/to/file.shp")
        result = _ensure_path_string(input_path)
        self.assertEqual(result, str(input_path))

    @patch('arcgis.features.geo._io.fileops.USE_ARCPY', True)
    def test_ensure_path_string_input_is_feature_layer_with_arcpy(self):
        mock_layer = MagicMock()
        mock_layer.connectionProperties = {'type': 'Feature Layer'}
        mock_layer.isWebLayer = False
        mock_layer.isFeatureLayer = True
        result = _ensure_path_string(mock_layer)
        self.assertEqual(result, mock_layer)

    @patch('arcgis.features.geo._io.fileops.USE_ARCPY', False)
    def test_ensure_path_string_input_feature_layer_without_arcpy_raises(self):
        mock_layer = MagicMock()
        mock_layer.connectionProperties = {'type': 'Feature Layer'}
        mock_layer.isWebLayer = False
        mock_layer.isFeatureLayer = True
        with self.assertRaises(ValueError) as context:
            _ensure_path_string(mock_layer)
        self.assertIn("requires the use of the ArcPy engine", str(context.exception))

    def test_ensure_path_string_invalid_input_raises(self):
        input_path = 12345  # Invalid type
        with self.assertRaises(ValueError) as context:
            _ensure_path_string(input_path)
        self.assertIn("Input path must be a string or a Path object", str(context.exception))

if __name__ == '__main__':
    unittest.main()
