import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from config import QALAB_ROOT_PATH


enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestCanReassignItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fp = QALAB_ROOT_PATH + r"\gis_mod_Item_cls\issue_10434.zip"
        cls.folder = cls.gis.content.folders._get_or_create("integration_test_gis_item_reassign")
        cls.item = cls.folder.add(
            item_properties={
                "title": "reassign_item_test",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            file=fp,
        ).result()
        cls.pitem = cls.item.publish(
            {
                "name": "reassign_item_test_publish",
                "tags": "integration_testing",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.pitem.delete(permanent=True)
        cls.item.delete(permanent=True)
        cls.folder.delete(permanent=True)

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
