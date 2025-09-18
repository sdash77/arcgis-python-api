import unittest
import pandas as pd
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from config import get_json_resource

proxies = None

data = get_json_resource("features/restaurants.json")


@profiles.agol
@integration_test
class TestFeatureLayerDeleteFeatures(unittest.TestCase):
    """
    Tests the FeatureLayer.delete_features operation
    """

    def test_delete_features_sync(self):
        """Tests the deletes_features operation with future=False"""
        item = None
        try:
            gis = self.gis
            sdf = pd.DataFrame(data)
            item = gis.content.import_data(
                sdf, title="delete_features_sync", tags="ntgrtn-tst"
            )
            flyr = item.layers[0]
            where = "FID=2"
            d = flyr.delete_features(
                deletes=None,
                where=where,
                rollback_on_failure=True,
                return_delete_results=True,
                future=False,
            )
            resp = d
            assert "deleteResults" in resp
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=True,
                return_delete_results=True,
                future=False,
            )
            assert "deleteResults" in resp
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=True,
                return_delete_results=False,
                future=False,
            )
            assert "success" in resp
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=False,
                return_delete_results=False,
                future=False,
            )
            assert "success" in resp
        except Exception as e:
            raise e
        finally:
            if item.related_items("Service2Data", "forward"):
                item.related_items("Service2Data", "forward")[0].delete(permanent=True)
            if item:
                item.delete(permanent=True)

    def test_delete_features_async(self):
        """Tests the deletes_features operation with future=True"""
        item = None
        try:
            gis = self.gis
            sdf = pd.DataFrame(data)
            item = gis.content.import_data(
                sdf, title="delete_features_async", tags="ntgrtn-tst"
            )
            flyr = item.layers[0]
            where = "FID=2"
            d = flyr.delete_features(
                deletes=None,
                where=where,
                rollback_on_failure=True,
                return_delete_results=True,
                future=True,
            )
            resp = d
            assert "status" in resp.result()
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=True,
                return_delete_results=True,
                future=True,
            )
            assert "status" in resp.result()
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=True,
                return_delete_results=False,
                future=True,
            )
            assert "status" in resp.result()
            resp = flyr.delete_features(
                deletes="1",
                where=None,
                rollback_on_failure=False,
                return_delete_results=False,
                future=True,
            )
            assert "status" in resp.result()
        except Exception as e:
            raise e
        finally:
            if item.related_items("Service2Data", "forward"):
                item.related_items("Service2Data", "forward")[0].delete(permanent=True)
            if item:
                assert item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
