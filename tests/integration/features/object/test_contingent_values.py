import shutil
import time
import unittest

import data_utils
from arcgis.features import FeatureLayer
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles
import utils.data_utils

# enable_verbose_logging()
FILE_PATH = QALAB_ROOT_PATH + r"\ContingentValues\CV_Gas_forTest.zip"


@profiles.enterprise_and_agol
@integration_test
class TestContingentValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """create and publish test item"""
        uid = int(time.time())
        layer_name = f"CV_Gas_1_issue_{uid}"
        item_type = data_utils.ItemType.FGDB.value
        cls.published_item = data_utils.publish_test_item(
            gis=cls.gis,
            layer_name=layer_name,
            source_data_path=FILE_PATH,
            item_type=item_type,
            prep_for_editing=False,
        )

    def test_contingent_values_fl(self):
        fl: FeatureLayer = self.published_item.layers[0]
        self.assertIsInstance(
            fl.contingent_values, dict, "Incorrect type for CV result"
        )
        self.assertIsInstance(fl.field_groups, dict, "Incorrect type for FG result")

    def test_contingent_values_fl_manager(self):
        fl: FeatureLayer = self.published_item.layers[0]
        mgr = fl.manager
        assert mgr.contingent_values
        assert mgr.field_groups

    @classmethod
    def tearDownClass(cls):
        data_utils.cleanup_published_items([cls.published_item])


if __name__ == "__main__":
    unittest.main()
