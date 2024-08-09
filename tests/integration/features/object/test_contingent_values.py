import os
import unittest
from arcgis.gis import GIS, Item, ContentManager, User, UserManager
from arcgis.features import FeatureLayer, FeatureLayerCollection
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()
FILE_PATH = QALAB_ROOT_PATH + r"\ContingentValues\CV_Gas.zip"


@profiles.enterprise
@integration_test
class TestContingentValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """create and publish test item"""
        items: list[Item] = cls.gis.content.search("CV_Gas")
        [item.delete() for item in items]
        items: list[Item] = cls.gis.content.search("CV_Gas")
        if len(items) == 0:
            cls.sditem_ent = cls.gis.content.add(
                item_properties={
                    "title": "CV_Gas",
                    "type": "File Geodatabase",
                    "tags": "gas",
                },
                data=FILE_PATH,
            )
            cls.pitem_ent = cls.sditem_ent.publish(
                publish_parameters={
                    "name": "CV_Gas",
                    "capabilities": "Create,Delete,Query,Update,Editing,Extract",
                }
            )

    def test_contingent_values_fl(self):
        fl: FeatureLayer = self.pitem_ent.layers[0]
        assert isinstance(fl.contingent_values, dict)
        assert isinstance(fl.field_groups, dict)

    def test_contingent_values_fl_manager(self):
        fl: FeatureLayer = self.pitem_ent.layers[0]
        mgr = fl.manager
        assert mgr.contingent_values
        assert mgr.field_groups

    @classmethod
    def tearDownClass(cls):
        cls.pitem_ent.delete()
        cls.sditem_ent.delete()


if __name__ == "__main__":
    unittest.main()
