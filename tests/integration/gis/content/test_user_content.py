#######################################################################
import unittest
import time
import os
from types import GeneratorType

from integration.config import QALAB_ROOT_PATH
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

        cls.uid = int(time.time())
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(cls.qalab_base_path, "gis_mod_Item_cls")
        cls.shapefile_data = "major_cities_shp.zip"

        cls.published_item = publish_test_item(
            gis=cls.gis,
            layer_name=f"major_cities_{cls.uid}",
            source_data_path=os.path.join(cls.qalab_cls_path, cls.shapefile_data),
            item_type=ItemTypeEnum.SHAPEFILE,
            prep_for_editing=False,
        )

        cls.user_list: list[User] = [
            user
            for user in cls.gis.users.search("NOT username:esri*")
            if len(list(user.folders)) > 1
        ]

    def test_user_folders(self):
        gis: GIS = self.gis
        if len(self.user_list) == 0:
            self.skipTest("No valid users, skipping")

        user: User = self.user_list[-1]
        self.published_item.reassign_to(user)
        folder_gen = user.folders
        assert isinstance(user.folders, GeneratorType)
        folder = next(folder_gen)
        assert isinstance(folder, Folder)
        assert folder.name == "Root Folder"
        assert len(list(folder.list(item_type=ItemTypeEnum.SHAPEFILE))) >= 1
        assert (
            len([i for i in user.items(folder) if i.title.startswith("major_cities_")])
            >= 2
        )
        pfolder = next(folder_gen)
        self.assertIsNotNone(pfolder.properties["id"], "Folder must have ID.")
        self.assertNotIn("name", pfolder.properties, "Only Root Folder has name key.")
        del folder_gen

    def test_user_groups(self):
        for user in self.user_list:
            if len(user.groups) > 0:
                break
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
