import os
import sys
import unittest
import pandas as pd
from arcgis.gis import GIS
from arcgis.layers._ogc import KMLLayer
from utils.decorators import integration_test

kml_url = "http://quickmap.dot.ca.gov/data/lcs.kml"


@integration_test
class TestKMLLayer(unittest.TestCase):
    """Tests working with a KML Layer"""

    def test_kml(self):
        """tests the KML Layer methods and properties"""
        kml = KMLLayer(url=kml_url)
        assert isinstance(kml, KMLLayer)
        assert kml.opacity == 1
        kml.opacity = 0.5
        assert kml.opacity == 0.5
        assert isinstance(kml.scale, tuple)
        kml.scale = (1, 2)
        assert kml.scale == (1, 2)
        assert isinstance(kml.title, str)
        kml.title = "test"
        assert kml.title == "test"
        assert kml._lyr_json
        assert kml.properties


if __name__ == "__main__":
    unittest.main()
