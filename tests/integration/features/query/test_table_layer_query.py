import os
import time
import unittest

from utils.data_utils import publish_test_item, cleanup_published_items
from integration.config import QALAB_ROOT_PATH, get_resource_path
from utils.decorators import integration_test, profiles
from arcgis.gis._impl._dataclasses._contentds import ItemTypeEnum


@profiles.enterprise_and_agol
@integration_test
class TestQueryTableLayer(unittest.TestCase):
    """Tests the Query Sub-set functionality of the Table class"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        get test data
        """
        uid = int(time.time())
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_FeatureLayer_cls"
        )
        source_data_path = get_resource_path(
            "mapping/restaurants.xlsx", unique_copy=True
        )
        table_name = f"table_layer_query_{uid}"
        cls.table_item = publish_test_item(
            cls.gis, table_name, source_data_path, ItemTypeEnum.MICROSOFT_EXCEL
        )

        cls.table_to_test = cls.table_item.tables[0]

    def test_query(self):
        df = self.table_to_test.query("1=1", as_df=True)
        assert len(df) >= 0
        fs = self.table_to_test.query("1=1", as_df=False)
        assert hasattr(fs, "features")

    def test_query_with_ids_only(self):
        total_count = self.table_to_test.estimates["count"]
        res = self.table_to_test.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=0
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == total_count

    def test_query_with_ids_only_and_offset(self):
        total_count = self.table_to_test.estimates["count"]
        res = self.table_to_test.query(
            where="1=1",
            return_ids_only=True,
            return_all_records=False,
            result_offset=10,
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == total_count - 10

    def test_query_with_ids_only_and_offset_and_count(self):
        res = self.table_to_test.query(
            where="1=1",
            return_ids_only=True,
            return_all_records=False,
            result_offset=10,
            result_record_count=5,
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == 5

    def test_query_with_object_ids(self):
        total_count = self.table_to_test.estimates["count"]
        object_ids = self.table_to_test.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=0
        )["objectIds"]
        object_ids_str = ",".join(map(str, object_ids))
        res = self.table_to_test.query(
            where="1=1", return_all_records=False, object_ids=object_ids_str
        )
        assert len(res.features) == total_count

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.table_item])


if __name__ == "__main__":
    unittest.main()
