#######################################################################
import unittest
import time
import os
from types import GeneratorType

from integration.config import QALAB_ROOT_PATH, get_resource_path
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from utils.data_utils import publish_test_item, cleanup_published_items
from arcgis.gis import GIS, User, Item, Group, Folder, ItemTypeEnum

enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestUserContentMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        uid = int(time.time())
        source_data_path = get_resource_path(
            "staging_data/USA_Major_Cities.zip",
            unique_copy=True,
        )

        cls.published_item = publish_test_item(
            cls.gis,
            layer_name=f"ntgrtn_tst_user_content_{uid}",
            source_data_path=source_data_path,
            item_type=ItemTypeEnum.SHAPEFILE,
        )

        cls.user_list: list[User] = [
            user
            for user in cls.gis.users.search("NOT username:esri*")
            if len(list(user.folders)) > 1
        ]

    def test_user_folders(self):
        gis: GIS = self.gis
        if not self.user_list:
            self.skipTest("No valid users, skipping")
        user: User = self.user_list[-1]
        self.published_item.reassign_to(user)
        self.assertNotEqual(
            self.published_item.owner,
            gis.users.me.username,
            "Item owner should be different than initial owner.",
        )
        folder_gen = user.folders
        assert isinstance(user.folders, GeneratorType)
        folder = next(folder_gen)
        assert isinstance(folder, Folder)
        assert folder.name == "Root Folder"
        assert len(list(folder.list(item_type=ItemTypeEnum.SHAPEFILE))) >= 1
        assert (
            len(
                [
                    i
                    for i in user.items(folder)
                    if i.title.startswith("ntgrtn_tst_user_content_")
                ]
            )
            >= 2
        )
        pfolder = next(folder_gen)
        self.assertIsNotNone(pfolder.properties["id"], "Folder must have ID.")
        self.assertNotIn("name", pfolder.properties, "Only Root Folder has name key.")
        del folder_gen

    def test_user_groups(self):
        user = next((user for user in self.user_list if len(user.groups) > 0), None)
        if not user:
            self.skipTest("No user who with groups configured.")
        assert isinstance(user.groups[0], Group)

    def test_user_items(self):
        user = self.user_list[-1]
        f = [fld for fld in user.folders if len(list(user.items(fld))) > 0][0]
        if not f:
            self.skipTest(f"No items in any folders for {user.username}.")
        assert isinstance(user.items(f), GeneratorType)
        assert isinstance(list(user.items(f))[0], Item)

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(items=[cls.published_item])


if __name__ == "__main__":
    unittest.main()
