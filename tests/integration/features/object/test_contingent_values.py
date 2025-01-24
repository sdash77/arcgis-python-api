import shutil
import time
import unittest
from arcgis.gis import GIS, Item, ContentManager, User, UserManager
from arcgis.features import FeatureLayer, FeatureLayerCollection
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


# enable_verbose_logging()
FILE_PATH = QALAB_ROOT_PATH + r"\ContingentValues\CV_Gas_forTest.zip"


@profiles.enterprise_and_agol
@integration_test
class TestContingentValues(unittest.TestCase):
    pitem_ent = None
    sditem_ent = None

    @classmethod
    def setUpClass(cls):
        """create and publish test item"""
        uid = int(time.time())
        cls.sditem_ent = cls.gis.content.add(
            item_properties={
                "title": f"CV_Gas_1_issue_{uid}",
                "type": "File Geodatabase",
                "tags": "ntgrtn-tst",
            },
            data=FILE_PATH,
        )
        cls.pitem_ent = cls.sditem_ent.publish(
            publish_parameters={
                "name": f"CV_Gas_1_issue_{uid}",
                "capabilities": "Create,Delete,Query,Update,Editing,Extract",
                "tags": "ntgrtn-tst",
            }
        )

    def test_contingent_values_fl(self):
        fl: FeatureLayer = self.pitem_ent.layers[0]
        self.assertIsInstance(
            fl.contingent_values, dict, "Incorrect type for CV result"
        )
        self.assertIsInstance(fl.field_groups, dict, "Incorrect type for FG result")

    def test_contingent_values_fl_manager(self):
        fl: FeatureLayer = self.pitem_ent.layers[0]
        mgr = fl.manager
        assert mgr.contingent_values
        assert mgr.field_groups

    @classmethod
    def tearDownClass(cls):
        if cls.pitem_ent:
            cls.pitem_ent.delete(permanent=True)
        if cls.sditem_ent:
            cls.sditem_ent.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
