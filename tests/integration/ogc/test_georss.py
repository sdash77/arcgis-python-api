import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.mapping.ogc import GeoRSSLayer
geo_rss_url = "https://arcgis.github.io/arcgis-samples-javascript/sample-data/layers-georss/sample-georss.xml"

class TestGeoRSSLayer(unittest.TestCase):
    """Tests working with a GeoRss Layer"""
    def test_georss(self):
        """tests the georss methods and properties"""
        georss = GeoRSSLayer(url=geo_rss_url)
        assert isinstance(georss, GeoRSSLayer)
        assert georss.line_symbol
        assert georss.opacity == 0
        georss.opacity = .5
        assert georss.opacity == .5
        assert georss.point_symbol
        assert georss.polygon_symbol
        assert isinstance(georss.scale, tuple)
        georss.scale = (1,2)
        assert georss.scale == (1,2)
        assert isinstance(georss.title, str)
        georss.title = 'test'
        assert georss.title == 'test'
        assert georss._esri_json

if __name__ == "__main__":
    unittest.main()