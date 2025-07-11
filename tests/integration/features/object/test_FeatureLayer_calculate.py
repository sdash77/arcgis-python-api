import os
import time
import unittest
import concurrent.futures
from arcgis.gis import ContentManager
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items
from arcgis.gis._impl._dataclasses._contentds import ItemTypeEnum


@profiles.all
@integration_test
class TestFeatureLayerCalculate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path,
            "features_mod_FeatureLayer_calculate_cls",
            "calculate_sd.zip",
        )

        uid = int(time.time())
        layer_name = f"calculate_sd_{uid}"
        item_type = ItemTypeEnum.FILE_GEODATABASE
        cls.published_item = publish_test_item(
            gis=cls.gis,
            layer_name=layer_name,
            source_data_path=cls.qalab_cls_path,
            item_type=item_type,
            prep_for_editing=False,
        )

    def test_calculate_basic(self):
        """tests a simple calculate method"""
        fl = self.published_item.layers[0]
        field_to_update = [
            f for f in fl.properties.fields if f.name.upper() == "FIPS_CNTRY"
        ][0]
        field_to_update = field_to_update.name
        res = fl.calculate(
            where="ObjectID < 519",
            calc_expression={"field": field_to_update, "value": "R1"},
            future=False,
        )
        verify_update = fl.query(where=f"{field_to_update} = 'R1'")
        self.assertTrue(
            len(verify_update.features), "No results from calculated attribute."
        )

    def test_calculate_async(self):
        """tests a simple calculate method using the asynchronous method"""
        fl = self.published_item.layers[0]
        field_to_update = [
            f for f in fl.properties.fields if f.name.upper() == "FIPS_CNTRY"
        ][0]
        field_to_update = field_to_update.name
        res = fl.calculate(
            where="ObjectID < 519",
            calc_expression={"field": field_to_update, "value": "R1"},
            future=True,
        )
        self.assertIsNotNone(res, "No result returned")
        self.assertIsInstance(
            res, concurrent.futures.Future, "Result is not a <Future> instance"
        )
        self.assertTrue(res.result(), "Incorrect async result")
        verify_update = fl.query(where=f"{field_to_update} = 'R1'")
        self.assertTrue(
            len(verify_update.features), "No results from calculated attribute."
        )

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.published_item])


if __name__ == "__main__":
    unittest.main()
