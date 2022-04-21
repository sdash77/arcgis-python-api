import logging
import sys
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\tests")
import unittest
from arcgis.features._utility import UtilityNetworkManager
from arcgis.features._version import Version
from arcgis.gis import GIS
import json

with open(r"tests\integration\features\services_config.json") as json_data_file:
    data = json.load(json_data_file)

gis = GIS(data["utility_network"]["url"], data["utility_network"]["username"], data["utility_network"]["password"])
version = Version("https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Oracle/FeatureServer", gis)
utility_net = UtilityNetworkManager("https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Oracle/FeatureServer/500001", version, gis)
class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def add_product(self):
        """ Test `add_product` method on a utility service."""



if __name__ == "__main__":
    unittest.main()