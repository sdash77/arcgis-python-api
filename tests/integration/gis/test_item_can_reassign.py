import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from config import QALAB_ROOT_PATH


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestCanReassignItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fp = QALAB_ROOT_PATH + r"\gis_mod_Item_cls\issue_10434.zip"
        cls.item = cls.gis.content.add(
            item_properties={
                "title": "reassign_item_test",
                "type": "Shapefile",
            },
            data=fp,
        )
        cls.pitem = cls.item.publish(
            {
                "name": "reassign_item_test",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.pitem.delete()
        cls.item.delete()

    def test_can_reassign(self):
        """tests the new reassign operation"""
        items = [self.item, self.pitem]
        for item in items:
            for user in self.gis.users.search("*")[:3]:
                assert isinstance(
                    item.can_reassign(target_user=user.username), tuple
                )
                assert isinstance(item.can_reassign(target_user=user), tuple)


if __name__ == "__main__":
    unittest.main()
