import os
import unittest
import pandas as pd
from arcgis.gis import GIS
from arcgis.layers._ogc import OGCCollection, OGCFeatureService
from collections.abc import Iterable as _Iterable
from utils.decorators import integration_test

ogc_url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/structures_medical_emergency_response_ogc/OGCFeatureServer"


@integration_test
class TestOGCFS(unittest.TestCase):
    """Tests working with a OGC FS and Layer"""

    def test_ogc_fs(self):
        """tests the ogc fs methods and properties"""
        ogc = OGCFeatureService(url_or_item=ogc_url)
        assert isinstance(ogc, OGCFeatureService)
        assert ogc.properties
        assert ogc.conformance
        assert isinstance(ogc.collections, _Iterable)

    def test_ogc_layer(self):
        """test the ogc layer methods/functions/proeprties"""
        ogc = OGCFeatureService(url_or_item=ogc_url)
        for ogclyr in ogc.collections:
            assert isinstance(ogclyr, OGCCollection)
            assert ogclyr.properties
            sedf = ogclyr.query(return_all=True)
            assert isinstance(sedf, pd.DataFrame)
            assert len(ogclyr.query(return_all=False, limit=10)) == 10
            assert isinstance(
                ogclyr.query(return_all=False, limit=10, as_dict=True), dict
            )
            assert len(ogclyr.query(return_all=True, as_dict=True)["features"]) == len(
                sedf
            )
            assert isinstance(ogclyr.get(2180), dict)
            break


if __name__ == "__main__":
    unittest.main()
