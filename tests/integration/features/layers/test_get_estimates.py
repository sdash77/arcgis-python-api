import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import unittest
from utils.decorators import integration_test, profiles
from utils.data_utils import cleanup_published_items

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


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerGetEstimates(unittest.TestCase):
    """tests the get estimates property on HFL"""

    def test_HFL_get_estimates_new_layer(self):
        """tests the call on a HFL for the get estimates if the property is not known to exist.
        this will depend on the version of enterprise you are using. Estimates is supported
        starting at 10.9.1"""

        item = None
        try:
            sdf = pd.DataFrame(data=DATA)
            sdf.spatial.set_geometry("SHAPE")
            item = self.gis.content.import_data(sdf, {"tags": "ntgrtn-tst"})
            # if unsupported, estimates returns an empty dict
            assert item.layers[0].estimates == {} or item.layers[0].estimates
        finally:
            if item:
                item.delete(permanent=True)

    def test_HFL_get_estimates_supported(self):
        """tests the HFL get estimates endpoints"""
        url = "https://servicesdev.arcgis.com/01ClFLufh9nZafWR/arcgis/rest/services/tblfc_gdb/FeatureServer/0"
        fl = FeatureLayer(url)
        assert fl.estimates


if __name__ == "__main__":
    unittest.main()
