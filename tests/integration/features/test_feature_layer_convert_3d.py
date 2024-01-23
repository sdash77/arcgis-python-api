import sys

# sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
import os
import unittest

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from utils.decorators import integration_test

gis = GIS(profile="your_dev_profile", verify_cert=False)

layer = FeatureLayer(
    "https://servicesdev.arcgis.com/5xC5Wrapp1gUAl2r/arcgis/rest/services/CUBE_WGS84_APIforPython/FeatureServer/0"
)


@integration_test
class TestConvert3DFeatureLayer(unittest.TestCase):
    def test_convert_3d(self):
        """
        Test the convert_3d method for assets on the layer
        """
        assets = [
            {
                "assetName": "null",
                "assetHash": "d7facaf8526acb749214d05d0ee5fc28145b013d2906edf1fc3baef81f0ae509",
            }
        ]

        resp = layer.convert_3d(assets, "3D_glb")
        assert resp


if __name__ == "__main__":
    unittest.main()
