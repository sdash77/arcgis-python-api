import sys
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")

from arcgis.gis import GIS
import unittest
from arcgis.features._topographic import TopographicProductionManager
from arcgis.features._version import VersionManager
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server.catalog import ServicesDirectory


url = "https://rextapilnxsvr01.esri.com/server"
username = "siteadmin"
password = "esri.agp2"
sd = ServicesDirectory(
    url=url,
    username=username,
    password=password,
    verify_cert=False,
)
topo = TopographicProductionManager("https://rextapilnxsvr01.esri.com/server/rest/services/MPS_AOI/TopographicProductionServer", sd)
topo.products()
class TestTopographicProductionManager(unittest.TestCase):
    """Tests the Topographic Production Service"""
    def get_products(self):
        products = topo.products()
        assert products

    def add_product(self):
        """ Test the add_product method """

        product = {
            "version": 0,
            "name": "ExampleProduct",
            "type": "MTM",
            "gridType": "TM50",
            "description": "Test Masking Product",
            "sheetIDField": "NRN",
            "productVersions": [
                {
                    "name": "TRD_4_5",
                    "template": "MTM50_Layout.pagx"
                }
            ],
            "resources": [
            {
                "name": "SourceWorkspace",
                "type": 3,
                "value": ""
            },
            {
                "name": "AOILayer",
                "type": 2,
                "value": ""
            },
            {
                "name": "SheetID",
                "type": 1,
                "value": ""
            },
            {
                "name": "Layout",
                "type": 6,
                "value": ""
            },
            {
                "name": "ProductFiles",
                "type": 7,
                "value": ""
            }
            ],
            "operations": [
            {
                "name": "MapResource",
                "type": 11,
                "description": "Update BaseMap DataSources",
                "parameters": [
                    {
                        "name": "in_map",
                        "value": "BaseMap"
                    }
                ]
            },   
        ]
        }
        topo.add_product(product)

if __name__ == "__main__":
    unittest.main()