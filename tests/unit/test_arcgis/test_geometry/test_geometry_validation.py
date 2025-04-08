import unittest
from arcgis.geometry import Geometry, Point, Polyline, Polygon, Envelope

class TestGeometryValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_point = Point({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
        cls.invalid_point = Geometry({"x": 2.22, "y": -1.5})  # Missing spatialReference
        cls.valid_polyline = Polyline({
            "paths": [[[-118.15, 33.80], [-118.20, 34.00]]],
            "spatialReference": {"wkid": 4326},
        })
        cls.invalid_polyline = Polyline({"paths": []})  # Empty paths
        cls.valid_polygon = Polygon({
            "rings": [[[0, 0], [1, 1], [1, 0], [0, 0]]],
            "spatialReference": {"wkid": 4326},
        })
        cls.invalid_polygon = Polygon({"rings": [[[0, 0], [1, 1], [1, 0]]]})  # Not closed
        cls.valid_envelope = Envelope({
            "xmin": 0, "ymin": 0, "xmax": 10, "ymax": 10, "spatialReference": {"wkid": 4326}
        })
        cls.invalid_envelope = Envelope({"xmin": 0, "ymin": 0, "xmax": None, "ymax": 10})  # Missing xmax
    
    def test_valid_point(self):
        self.assertTrue(self.valid_point.is_valid())
    
    def test_invalid_point(self):
        self.assertFalse(self.invalid_point.is_valid())
    
    def test_valid_polyline(self):
        self.assertTrue(self.valid_polyline.is_valid())
    
    def test_invalid_polyline(self):
        self.assertFalse(self.invalid_polyline.is_valid())
    
    def test_valid_polygon(self):
        self.assertTrue(self.valid_polygon.is_valid())
    
    def test_invalid_polygon(self):
        self.assertFalse(self.invalid_polygon.is_valid())
    
    def test_valid_envelope(self):
        self.assertTrue(self.valid_envelope.is_valid())
    
    def test_invalid_envelope(self):
        self.assertFalse(self.invalid_envelope.is_valid())

class TestCurvedGeometries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curve_polyline = Polyline(
            {
                "paths": [
                    [
                        {"x": -100, "y": 35},  # Start point
                        {
                            "curve": [
                                {"x": -95, "y": 37},  # Control point
                                {"x": -90, "y": 35},  # End point
                            ]
                        },
                    ]
                ],
                "spatialReference": {"wkid": 4326},
            }
        )

        cls.curve_polygon = Polygon(
            {
                "curveRings": [
                    [
                        {"x": -100, "y": 35},  # Start point
                        {
                            "curve": {
                                "a": {"x": -95, "y": 37},  # Control point
                                "b": {"x": -90, "y": 35},  # End point
                                "r": 5,  # Radius of the curve
                            }
                        },
                        {"x": -100, "y": 35},  # Closing the ring
                    ]
                ],
                "spatialReference": {"wkid": 4326},
            }
        )

    def test_curve_path_invalid(self):
        """Ensure curvePath is handled correctly by _is_valid()"""
        self.assertFalse(self.curve_polyline.is_valid())

    def test_curve_rings_invalid(self):
        """Ensure curveRings is handled correctly by _is_valid()"""
        self.assertFalse(self.curve_polygon.is_valid())

if __name__ == "__main__":
    unittest.main()
