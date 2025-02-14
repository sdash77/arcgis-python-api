import os
import unittest
import uuid
from arcgis.gis import Item, Group, ItemProperties, ItemTypeEnum
from arcgis.gis._impl._jb import StatusJob
from utils.decorators import integration_test, profiles, from_to_profiles
from integration.config import QALAB_ROOT_PATH


fp = os.path.join(QALAB_ROOT_PATH, "group_manager_data", "parkinglots.zip")


@profiles.admin_enterprise_and_k8s
@integration_test
class TestGroupExport(unittest.TestCase):
    """Tests Group Export using GroupMigrationManager"""

    @classmethod
    def setUpClass(cls):
        """setup item and group, and share item to group"""
        # create item
        cls.item = add_item_to_portal(cls.gis, fp, "group_export_item", ItemTypeEnum.SHAPEFILE)
        assert isinstance(cls.item, Item)

        # create group
        cls.export_group = cls.gis.groups.create(
            title=f"export_group_{uuid.uuid4().hex[:4]}",
            tags="integration_testing",
        )
        assert isinstance(cls.export_group, Group)

        # add item to group
        cls.item.sharing.groups.add(cls.export_group)

    def test_group_export_async(self):
        """tests exporting group items asynchronously"""
        self.epk_job = self.export_group.migration.create(
            items=[self.item], future=True
        )
        assert isinstance(self.epk_job, StatusJob)

        self.epk_item = self.epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_group_export_sync(self):
        """tests exporting group items synchronously"""
        self.epk_item = self.export_group.migration.create(
            items=[self.item], future=False
        )
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_group_export_to_folder(self):
        """tests exporting group items to specified folder"""
        if self.gis.version < [2024, 2]:
            self.skipTest("Export to folder is only supported in ArcGIS Enterprise 11.4 and later")

        self.epk_job = self.export_group.migration.create(
            items=[self.item], export_folder=self.gis.content.folders.get(),
        )
        assert isinstance(self.epk_job, StatusJob)

        self.epk_item = self.epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"
        assert self.epk_item in list(self.gis.content.folders.get().list())

    def test_group_export_output_filename(self):
        """tests exporting group items with specified output filename"""
        if self.gis.version < [2024, 1]:
            self.skipTest("output_filename is only supported in ArcGIS Enterprise 11.3 and later")

        self.epk_job = self.export_group.migration.create(
            items=[self.item], output_filename="test_group_import_export_epk"
        )
        assert isinstance(self.epk_job, StatusJob)

        self.epk_item = self.epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"
        assert self.epk_item.title == "test_group_import_export_epk.epk"

    def test_inspect_package(self):
        """tests the `inspect` package call on Portal"""
        self.epk_item = self.export_group.migration.create(
            items=[self.item], future=False
        )
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

        res = self.export_group.migration.inspect(self.epk_item)
        assert isinstance(res, dict)
        assert res['results'][0]['id'] == self.item.id

    @classmethod
    def tearDownClass(cls):
        """delete items, folders and groups"""
        delete_folder_and_item([cls.gis], ["group_export_import_", "exports"])
        delete_group([cls.gis], ["export_group_"])


@from_to_profiles.all_except_agol
@integration_test
# TODO: add tests for folder_owner, folder_name, and keep_epk_item for Enterprise 11.4 and later
class TestGroupImport(unittest.TestCase):
    """tests the group export import workflow using GroupMigrationManager"""

    @classmethod
    def setUpClass(cls):
        """setup item, groups and export epk item"""
        # create item in source gis
        cls.item = add_item_to_portal(cls.from_gis, fp, "group_export_item",  ItemTypeEnum.SHAPEFILE)
        assert isinstance(cls.item, Item)

        # create group in source gis
        cls.export_group = cls.from_gis.groups.create(
            title=f"export_group_{uuid.uuid4().hex[:4]}",
            tags="integration_testing",
        )
        assert isinstance(cls.export_group, Group)

        # add item to group in source gis
        cls.item.sharing.groups.add(cls.export_group)

        # export item to epk in source gis
        cls.epk_item = cls.export_group.migration.create(
            items=[cls.item], future=False
        )
        assert isinstance(cls.epk_item, Item)

        # get path of downloaded epk file
        cls.export_package_file = cls.epk_item.download()

        # create destination group in destination gis
        cls.import_group = cls.to_gis.groups.create(
            title=f"import_group_{uuid.uuid4().hex[:4]}",
            tags="integration_testing",
        )

    def test_group_import_to_different_gis(self):
        """tests importing group items"""
        if self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to a different gis")

        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        # add epk item in destination gis group
        epk_item = add_item_to_portal(
            self.to_gis, self.export_package_file, "import_group_epk", ItemTypeEnum.EXPORT_PACKAGE
        )
        assert isinstance(epk_item, Item)

        # add item to destination group
        epk_item.sharing.groups.add(self.import_group)

        # load item
        res = self.import_group.migration.load(epk_item)
        assert res
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)

    def test_group_import_to_same_gis_overwrite(self):
        """tests importing group items in same gis"""
        if not self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to same gis")

        res = self.import_group.migration.load(self.epk_item, overwrite=True)
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)

    def test_group_import_with_item_id(self):
        """tests importing multiple group items with item id specified"""
        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        try:
            # TODO: add the below package to new k8s portal
            self.epk_item = self.from_gis.content.search(
                query="owner:esri_notebook",
                item_type="Export Package",
                outside_org=True,
            )[0]

            import_group_content = self.import_group.migration.load(
                epk_item=self.epk_item,
                item_ids=["72224efc9e044001934bb3be87120beb"],
                overwrite=True,
                keep_epk_item=True,
            )
            r = import_group_content.result()
            assert "itemsSkipped" in r
            assert "itemsFailedImport" in r
        except Exception as e:
            raise e

    def test_group_import_with_folder_id(self):
        """tests importing group items with specified folder id"""
        if self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to a different gis")

        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        # add epk item in destination gis group
        epk_item = add_item_to_portal(
            self.to_gis, self.export_package_file, "import_group_epk", ItemTypeEnum.EXPORT_PACKAGE
        )
        assert isinstance(epk_item, Item)

        # add item to destination group
        epk_item.sharing.groups.add(self.import_group)

        # load item
        res = self.import_group.migration.load(epk_item=epk_item, folder_id="/")
        assert res
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)
        assert res.result()['itemsImported'][0].delete(permanent=True)

    @classmethod
    def tearDownClass(cls):
        """delete items, folders and groups"""
        delete_folder_and_item(
            [cls.from_gis, cls.to_gis], ["group_export_import_", "imports_", "exports"]
        )
        delete_group(
            [cls.from_gis, cls.to_gis], ["export_group_", "import_group_"]
        )


def add_item_to_portal(gis, path, title, item_type):
    """helper function to add shapefile/epk item to portal"""
    folder = gis.content.folders._get_or_create(
        "group_export_import_integration_testing"
    )
    item_properties = ItemProperties(
        title=f"{title}_{uuid.uuid4().hex[:4]}",
        item_type=item_type.value,
        tags=["integration_testing"],
    )
    item = folder.add(item_properties, file=path).result()
    return item


def delete_folder_and_item(gis_list, folder_name_list):
    """helper function to delete items, folders"""
    for gis in gis_list:
        folder_list = list(gis.content.folders.list())
        for folder in folder_list:
            if any(name in folder.name for name in folder_name_list):
                if len(list(folder.list("*"))) == 0:
                    folder.delete()
                else:
                    for import_item in folder.list("*"):
                        import_item.delete(permanent=True)
                    folder.delete()


def delete_group(gis_list, group_name_list):
    """helper function to delete groups"""
    for gis in gis_list:
        group_list = gis.groups.search("*")
        for group in group_list:
            if any(name in group.title for name in group_name_list):
                group.delete()


if __name__ == "__main__":
    unittest.main()
