import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.mapping.ogc import GeoJSONLayer
geo_rss_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

class TestGeoRSSLayer(unittest.TestCase):
    """Tests working with a GeoJSON Layer"""
    def test_geojson(self):
        """tests the georss methods and properties"""
        georss = GeoJSONLayer(url=geo_rss_url)
        assert isinstance(georss, GeoJSONLayer)

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