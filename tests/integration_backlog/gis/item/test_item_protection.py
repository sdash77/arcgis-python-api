import sys
import unittest
import pandas as pd
from arcgis.gis import GIS
from utils.decorators import integration_test

PROFILES = ["your_online_admin_profile", "your_ent_admin_profile"]
DATA = [
    {
        "ADMIN_NAME": "Mato Grosso",
        "CITY_NAME": "Cuiaba",
        "CNTRY_NAME": "Brazil",
        "FIPS_CNTRY": "BR",
        "GMI_ADMIN": "BRA-MGR",
        "Id": 0,
        "LABEL_FLAG": 0,
        "OBJECTID_1": 1,
        "ObjectID": 0,
        "POP": 521934,
        "POP_CLASS": "500,000 to 999,999",
        "POP_RANK": 3,
        "PORT_ID": 0,
        "SHAPE": {
            "x": -6244244.6062,
            "y": -1760180.1805000007,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
        "STATUS": "Provincial capital",
    },
    {
        "ADMIN_NAME": "Kentucky",
        "CITY_NAME": "Frankfort",
        "CNTRY_NAME": "United States",
        "FIPS_CNTRY": "US",
        "GMI_ADMIN": "USA-KEN",
        "Id": 0,
        "LABEL_FLAG": 0,
        "OBJECTID_1": 2,
        "ObjectID": 500,
        "POP": 16315,
        "POP_CLASS": "Less than 50,000",
        "POP_RANK": 7,
        "PORT_ID": 0,
        "SHAPE": {
            "x": -9444234.6816,
            "y": 4607859.9877,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
        "STATUS": "Provincial capital",
    },
    {
        "ADMIN_NAME": "Tennessee",
        "CITY_NAME": "Nashville",
        "CNTRY_NAME": "United States",
        "FIPS_CNTRY": "US",
        "GMI_ADMIN": "USA-TNN",
        "Id": 0,
        "LABEL_FLAG": 0,
        "OBJECTID_1": 3,
        "ObjectID": 501,
        "POP": 530852,
        "POP_CLASS": "500,000 to 999,999",
        "POP_RANK": 3,
        "PORT_ID": 0,
        "SHAPE": {
            "x": -9664535.075,
            "y": 4320178.250500001,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
        "STATUS": "Provincial capital",
    },
    {
        "ADMIN_NAME": "Distrito Federal",
        "CITY_NAME": "Brasilia",
        "CNTRY_NAME": "Brazil",
        "FIPS_CNTRY": "BR",
        "GMI_ADMIN": "BRA-DFD",
        "Id": 0,
        "LABEL_FLAG": 0,
        "OBJECTID_1": 4,
        "ObjectID": 1,
        "POP": 2207718,
        "POP_CLASS": "1,000,000 to 4,999,999",
        "POP_RANK": 2,
        "PORT_ID": 0,
        "SHAPE": {
            "x": -5331952.8794,
            "y": -1780660.5108999982,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
        "STATUS": "National and provincial capital",
    },
    {
        "ADMIN_NAME": "Goias",
        "CITY_NAME": "Goiania",
        "CNTRY_NAME": "Brazil",
        "FIPS_CNTRY": "BR",
        "GMI_ADMIN": "BRA-GOI",
        "Id": 0,
        "LABEL_FLAG": 0,
        "OBJECTID_1": 5,
        "ObjectID": 2,
        "POP": 1171195,
        "POP_CLASS": "1,000,000 to 4,999,999",
        "POP_RANK": 2,
        "PORT_ID": 0,
        "SHAPE": {
            "x": -5483041.6975,
            "y": -1889069.6970999986,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
        "STATUS": "Provincial capital",
    },
]


@integration_test
class TestItemProtection(unittest.TestCase):
    """tests for Item Protection (BUG-000136586)"""

    def test_protection_item_get(self):
        """tests protecting and item by getting the item using gis.content.get()"""
        sdf = pd.DataFrame(DATA)
        sdf.spatial.set_geometry("SHAPE")
        for profile in PROFILES:
            gis = GIS(profile=profile)
            item = gis.content.import_data(sdf)
            item_test = gis.content.get(item.itemid)
            assert item_test
            assert item_test.protect(enable=True)["success"]
            assert item_test.protect(enable=False)["success"]
            assert item.delete()

    def test_protection_item_search(self):
        """tests protecting and item by getting the item using gis.content.get()"""
        sdf = pd.DataFrame(DATA)
        sdf.spatial.set_geometry("SHAPE")
        for profile in PROFILES:
            gis = GIS(profile=profile)
            item = gis.content.import_data(sdf)
            item_test = gis.content.search(f"id: {item.itemid}")[0]
            assert item_test
            assert item_test.protect(enable=True)["success"]
            assert item_test.protect(enable=False)["success"]
            assert item.delete()


if __name__ == "__main__":
    unittest.main()
