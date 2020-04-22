import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.mapping.ogc import KMLLayer
geo_rss_url = "http://quickmap.dot.ca.gov/data/lcs.kml"

class TestKMLLayer(unittest.TestCase):
    """Tests working with a KML Layer"""
    def test_kml(self):
        """tests the KML Layer methods and properties"""
        georss = KMLLayer(url=geo_rss_url)
        assert isinstance(georss, KMLLayer)
        assert georss.opacity == 0
        georss.opacity = .5
        assert georss.opacity == .5
        assert isinstance(georss.scale, tuple)
        georss.scale = (1,2)
        assert georss.scale == (1,2)
        assert isinstance(georss.title, str)
        georss.title = 'test'
        assert georss.title == 'test'
        assert georss._esri_json

if __name__ == "__main__":
    unittest.main()