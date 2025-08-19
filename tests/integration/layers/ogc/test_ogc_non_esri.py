import unittest
import pandas as pd
from arcgis.layers import OGCCollection, OGCFeatureService

from utils.decorators import integration_test

ogc_url = "https://demo.ldproxy.net/daraa"
ogc_collection_url = "https://demo.ldproxy.net/daraa/collections/AeronauticCrv"


@integration_test
class TestOGCFSNonEsri(unittest.TestCase):
    """Tests working with a OGC FS and Layer"""

    def test_ogc_fs(self):
        """tests the ogc fs methods and properties"""
        ogc = OGCFeatureService(url=ogc_url)
        assert isinstance(ogc, OGCFeatureService)
        assert ogc.properties
        assert ogc.conformance

        endpoints = ["core", "oas30", "html", "geojson"]
        conformance_urls = [
            True
            for e in endpoints
            for u in ogc.conformance.get("conformsTo")
            if u.endswith(e)
        ]
        self.assertEqual(
            10,
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
            dict_query = ogc_lyr.query(return_all=False, limit=10, as_dict=True)
            self.assertIsInstance(
                dict_query, dict, "Query non-esri OGC with as_dict failed"
            )
            assert len(ogc_lyr.query(return_all=True, as_dict=True)["features"]) == len(
                sedf
            )
            assert isinstance(ogc_lyr.get(8), dict)
            break

    def test_ogc_collection(self):
        ogc_collection = OGCCollection(url=ogc_collection_url)
        self.assertEqual(
            "Aeronautic (Curves)",
            ogc_collection.properties.get("title"),
            "Unexpected OGC Collection title.",
        )


if __name__ == "__main__":
    unittest.main()
