import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.gis.ogc import WMSLayer
geo_rss_url = "http://ows.mundialis.de/services/service"

class TestWMSLayer(unittest.TestCase):
    """Tests working with a WMS Layer"""
    def test_wms(self):
        """tests the WMS Layer methods and properties"""
        georss = WMSLayer(url=geo_rss_url)
        assert isinstance(georss, WMSLayer)
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