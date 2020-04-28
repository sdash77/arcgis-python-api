import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.mapping.ogc import WMSLayer
wm_url = "http://ows.mundialis.de/services/service"

class TestWMSLayer(unittest.TestCase):
    """Tests working with a WMS Layer"""
    def test_wms(self):
        """tests the WMS Layer methods and properties"""
        wms = WMSLayer(url=wm_url)
        assert isinstance(wms, WMSLayer)
        assert wms.opacity == 0
        wms.opacity = .5
        assert wms.opacity == .5
        assert isinstance(wms.scale, tuple)
        wms.scale = (1,2)
        assert wms.scale == (1,2)
        assert isinstance(wms.title, str)
        wms.title = 'test'
        assert wms.title == 'test'
        assert wms._esri_json
        assert wms.properties

if __name__ == "__main__":
    unittest.main()