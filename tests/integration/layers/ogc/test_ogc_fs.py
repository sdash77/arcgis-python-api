import unittest
import pandas as pd
from arcgis.layers import OGCCollection, OGCFeatureService
from collections.abc import Iterable as _Iterable
from utils.decorators import integration_test

ogc_url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/structures_medical_emergency_response_ogc/OGCFeatureServer"
ogc_collection_url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/structures_medical_emergency_response_ogc/OGCFeatureServer/collections/0"


@integration_test
class TestOGCFS(unittest.TestCase):
    """Tests working with a OGC FS and Layer"""

    def test_ogc_fs(self):
        """tests the ogc fs methods and properties"""
        ogc = OGCFeatureService(url=ogc_url)
        assert isinstance(ogc, OGCFeatureService)
        assert ogc.properties
        assert ogc.conformance
        assert isinstance(ogc.collections, _Iterable)
        endpoints = ["core", "oas30", "html", "geojson"]
        conformance_urls = [
            True
            for e in endpoints
            for u in ogc.conformance.get("conformsTo")
            if u.endswith(e)
        ]
        self.assertEqual(
            4,
            len(conformance_urls),
            f"Incorrect count of conformance endpoints. Got {len(conformance_urls)}",
        )

    def test_ogc_layer(self):
        """test the ogc layer methods/functions/properties"""
        ogc = OGCFeatureService(url=ogc_url)
        for ogc_lyr in ogc.collections:
            assert isinstance(ogc_lyr, OGCCollection)
            assert ogc_lyr.properties
            sedf = ogc_lyr.query(return_all=True)
            assert isinstance(sedf, pd.DataFrame)
            assert len(ogc_lyr.query(return_all=False, limit=10)) == 10
            assert isinstance(
                ogc_lyr.query(return_all=False, limit=10, as_dict=True), dict
            )
            assert len(ogc_lyr.query(return_all=True, as_dict=True)["features"]) == len(
                sedf
            )
            assert isinstance(ogc_lyr.get(2180), dict)
            break

    def test_ogc_collection(self):
        ogc_collection = OGCCollection(url=ogc_collection_url)
        self.assertEqual(
            "Hospitals_Medical_Centers",
            ogc_collection.properties.get("title"),
            "Unexpected OGC Collection title.",
        )


if __name__ == "__main__":
    unittest.main()
