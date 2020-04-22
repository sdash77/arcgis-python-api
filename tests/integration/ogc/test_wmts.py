import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.mapping.ogc import WMTSLayer
wm_url = 'https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS/'

class TestwmtsLayer(unittest.TestCase):
    """Tests working with a wmts Layer"""
    def test_wmts(self):
        """tests the wmts Layer methods and properties"""
        wmts = WMTSLayer(url=wm_url)
        assert isinstance(wmts, WMTSLayer)
        assert wmts.opacity == 0
        wmts.opacity = .5
        assert wmts.opacity == .5
        assert isinstance(wmts.scale, tuple)
        wmts.scale = (1,2)
        assert wmts.scale == (1,2)
        assert isinstance(wmts.title, str)
        wmts.title = 'test'
        assert wmts.title == 'test'
        assert wmts._esri_json

if __name__ == "__main__":
    unittest.main()