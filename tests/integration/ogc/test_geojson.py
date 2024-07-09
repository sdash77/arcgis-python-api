import os
import sys
import unittest
import pandas as pd
from arcgis.gis import GIS
from arcgis.layers._ogc import GeoJSONLayer
from utils.decorators import integration_test

geo_rss_url = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
)


@integration_test
class TestGeoRSSLayer(unittest.TestCase):
    """Tests working with a GeoJSON Layer"""

    def test_geojson(self):
        """tests the georss methods and properties"""
        georss = GeoJSONLayer(url=geo_rss_url)
        assert isinstance(georss, GeoJSONLayer)
        assert georss.opacity == 1
        georss.opacity = 0.5
        assert georss.opacity == 0.5
        assert isinstance(georss.scale, tuple)
        georss.scale = (1, 2)
        assert georss.scale == (1, 2)
        assert isinstance(georss.title, str)
        georss.title = "test"
        assert georss.title == "test"
        assert georss._lyr_json
        assert georss.properties


if __name__ == "__main__":
    unittest.main()
