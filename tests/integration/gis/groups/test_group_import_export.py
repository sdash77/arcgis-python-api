import unittest
import uuid
from arcgis.gis import Item, Group, ItemProperties, ItemTypeEnum
from arcgis.gis._impl._jb import StatusJob
from utils.decorators import integration_test
from integration.config import QALAB_ROOT_PATH
import os
from utils.decorators import profiles, from_to_profiles


fp = os.path.join(QALAB_ROOT_PATH, "group_manager_data", "parkinglots.zip")


@profiles.admin_enterprise_and_k8s
@integration_test
class TestGroupExport(unittest.TestCase):
    """Tests the Group Export Method on a Group Object"""

    def setUp(self):
        """setup item and group, and share item to group"""

        # create item
        self.folder = self.gis.content.folders.get("group_export_integration_testing")
        item_properties = ItemProperties(
            title=f"test_group_import_export_{uuid.uuid4().hex[:4]}",
            item_type=ItemTypeEnum.SHAPEFILE.value,
            tags=["integration_testing"],
        )
        self.pitem = self.folder.add(item_properties, file=fp).result()
        isinstance(self.pitem, Item)

        self.new_group = self.gis.groups.create(
            title=f"export_test_group_{uuid.uuid4().hex[:4]}", tags="integration_testing"
        )
        isinstance(self.new_group, Group)

        self.pitem.sharing.groups.add(self.new_group)

    def tearDown(self):
        if self.pitem:
            assert self.pitem.delete(permanent=True)
        if self.new_group:
            assert self.new_group.delete()
        if self.epk_item:
            assert self.epk_item.delete(permanent=True)

    def test_group_export_async(self):
        """tests exporting the group items to an epk asynchronously"""
        self.epk_job = self.new_group.migration.create(
            items=[self.pitem], future=True
        )
        assert isinstance(self.epk_job, StatusJob)

        self.epk_item = self.epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_group_export_sync(self):
        """tests exporting the group items to an epk synchronously"""
        self.epk_item = self.new_group.migration.create(
            items=[self.pitem], future=False
        )
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_inspect_package(self):
        """tests the `inspect` package call on Portal"""
        self.epk_item = self.new_group.migration.create(
            items=[self.pitem], future=False
        )
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

        res = self.new_group.migration.inspect(self.epk_item)
        assert isinstance(res, dict)
        assert res['results'][0]['id'] == self.pitem.id


@from_to_profiles.all_except_agol
@integration_test
class TestGroupImport(unittest.TestCase):
    """tests the import methods"""

    def setUp(self):
        """setup item, group and export epk item"""

        # create item
        self.folder = self.from_gis.content.folders.get("group_export_integration_testing")
        item_properties = ItemProperties(
            title=f"test_group_import_export_{uuid.uuid4().hex[:4]}",
            item_type=ItemTypeEnum.SHAPEFILE.value,
            tags=["integration_testing"],
        )
        self.pitem = self.folder.add(item_properties, file=fp).result()
        isinstance(self.pitem, Item)

        # create group
        self.new_group = self.from_gis.groups.create(
            title=f"export_test_group_{uuid.uuid4().hex[:4]}", tags="integration_testing"
        )
        isinstance(self.new_group, Group)

        # add item to group
        self.pitem.sharing.groups.add(self.new_group)

        # export item
        self.epk_item = self.new_group.migration.create(
            items=[self.pitem], future=False
        )
        assert isinstance(self.epk_item, Item)
        self.export_package_file = self.epk_item.download()

    def tearDown(self):
        if self.pitem:
            assert self.pitem.delete(permanent=True)
        if self.new_group:
            assert self.new_group.delete()

    def test_group_import_to_different_gis(self):
        """tests importing the group items from an epk"""

        if self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to a different gis")

        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        # delete old test group in to_gis
        group_search_result = self.to_gis.groups.search("new_group1_dest")
        [group.delete() for group in group_search_result]

        # create group in to_gis
        group_dest = self.to_gis.groups.create(
            f"new_group1_dest_{uuid.uuid4().hex[:4]}", tags="integration_testing"
        )

        # create item from exported epk file in to_gis
        self.folder = self.to_gis.content.folders.get("group_export_integration_testing")
        item_properties = ItemProperties(
            title=f"test_group_import_export_add_epk_{uuid.uuid4().hex[:4]}",
            item_type=ItemTypeEnum.EXPORT_PACKAGE.value,
            tags=["integration_testing"],
        )
        new_item = self.folder.add(item_properties, file=self.export_package_file).result()
        assert isinstance(new_item, Item)

        # add item to group
        new_item.sharing.groups.add(group_dest)

        # load item
        m = group_dest.migration
        res = m.load(new_item)

        assert res
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)

        if group_dest:
            group_dest.delete()

    def test_group_import_to_same_gis(self):
        """tests importing the group items from an epk"""

        if not self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to same gis")

        res = self.new_group.migration.load(self.epk_item, overwrite=True)
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)    
    
    @classmethod
    def tearDownClass(cls):
        for gis in [cls.from_gis, cls.to_gis]:
            folder_list = list(gis.content.folders.list())
            for folder in folder_list:
                if folder.name.startswith("imports_") or folder.name.startswith("exports"):
                    if len(list(folder.list("*"))) == 0:
                        folder.delete()
                    else:
                        for import_item in folder.list("*"):
                            import_item.delete(permanent=True)
                        folder.delete()
                if folder.name == "exports":
                    for exp_item in folder.list(
                        item_type=ItemTypeEnum.EXPORT_PACKAGE.value
                    ):
                        exp_item.delete(permanent=True)
                    folder.delete()

if __name__ == "__main__":
    unittest.main()
