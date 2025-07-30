import os
import unittest
import uuid
from arcgis.gis import Item, Group, ItemTypeEnum
from arcgis.gis._impl._jb import StatusJob
from utils.decorators import integration_test, profiles, from_to_profiles
from integration.config import QALAB_ROOT_PATH
from utils.data_utils import add_source_item, create_group, cleanup_published_items, cleanup_groups, cleanup_folders

from integration.config import get_resource_path

fp = get_resource_path("staging_data/parkinglots.zip", unique_copy=True)


@profiles.admin_enterprise_and_k8s
@integration_test
class TestGroupExport(unittest.TestCase):
    """Tests Group Export using GroupMigrationManager"""

    @classmethod
    def setUpClass(cls):
        """setup item and group, and share item to group"""
        # create item
        cls.item = add_source_item(
            cls.gis, f"group_export_item_{uuid.uuid4().hex[:4]}", ItemTypeEnum.SHAPEFILE, fp
        )
        assert isinstance(cls.item, Item)

        # create group
        cls.export_group = create_group(cls.gis, f"export_group_{uuid.uuid4().hex[:4]}")
        assert isinstance(cls.export_group, Group)

        # add item to group
        cls.item.sharing.groups.add(cls.export_group)

        cls.epk_item = None

    def test_group_export_async(self):
        """tests exporting group items asynchronously"""
        epk_job = self.export_group.migration.create(items=[self.item], future=True)
        assert isinstance(epk_job, StatusJob)

        self.epk_item = epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_group_export_sync(self):
        """tests exporting group items synchronously"""
        self.epk_item = self.export_group.migration.create(items=[self.item], future=False)
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

    def test_group_export_to_folder(self):
        """tests exporting group items to specified folder"""
        if self.gis.version < [2024, 2]:
            self.skipTest("Export to folder is only supported in ArcGIS Enterprise 11.4 and later")

        epk_job = self.export_group.migration.create(items=[self.item], export_folder=self.gis.content.folders.get())
        assert isinstance(epk_job, StatusJob)

        self.epk_item = epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"
        assert self.epk_item in list(self.gis.content.folders.get().list())

    def test_group_export_output_filename(self):
        """tests exporting group items with specified output filename"""
        if self.gis.version < [2024, 1]:
            self.skipTest("output_filename is only supported in ArcGIS Enterprise 11.3 and later")

        epk_job = self.export_group.migration.create(items=[self.item], output_filename=f"test_group_import_export_epk")
        assert isinstance(epk_job, StatusJob)

        self.epk_item = epk_job.result()
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"
        assert self.epk_item.title == "test_group_import_export_epk.epk"

    def test_inspect_package(self):
        """tests the `inspect` package call on Portal"""
        self.epk_item = self.export_group.migration.create(items=[self.item], future=False)
        assert isinstance(self.epk_item, Item)
        assert self.epk_item.type == "Export Package"

        res = self.export_group.migration.inspect(self.epk_item)
        assert isinstance(res, dict)
        assert res['results'][0]['id'] == self.item.id

    def tearDown(self):
        """delete items, folders and groups"""
        cleanup_published_items([self.epk_item])

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.item])
        cleanup_groups([cls.export_group])
        cleanup_folders(cls.gis, ["imports_", "exports"])


@from_to_profiles.all_except_agol
@integration_test
# TODO: add tests for folder_owner, folder_name, and keep_epk_item for Enterprise 11.4 and later
class TestGroupImport(unittest.TestCase):
    """tests the group export import workflow using GroupMigrationManager"""

    @classmethod
    def setUpClass(cls):
        """setup item, groups and export epk item"""
        cls.item = add_source_item(
            cls.from_gis, f"group_import_item_{uuid.uuid4().hex[:4]}", ItemTypeEnum.SHAPEFILE, fp
        )
        assert isinstance(cls.item, Item)
        cls.export_group = create_group(cls.from_gis, f"export_group_{uuid.uuid4().hex[:4]}")
        assert isinstance(cls.export_group, Group)
        cls.item.sharing.groups.add(cls.export_group)

        # export item to epk in source gis
        cls.epk_item = cls.export_group.migration.create(items=[cls.item], future=False)
        assert isinstance(cls.epk_item, Item)
        cls.export_package_file = cls.epk_item.download()

        # create destination group in destination gis
        cls.import_group = create_group(cls.to_gis, f"import_group_{uuid.uuid4().hex[:4]}")

    def test_group_import_to_different_gis(self):
        """tests importing group items"""
        if self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to a different gis")

        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        # add epk item in destination gis group
        epk_item = add_source_item(
            self.to_gis, f"epk_{uuid.uuid4().hex[:4]}", ItemTypeEnum.EXPORT_PACKAGE, self.export_package_file
        )
        assert isinstance(epk_item, Item)

        # load item
        res = self.import_group.migration.load(epk_item)
        assert res
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)
        if res.result()['itemsImported']:
            cleanup_published_items(res.result()['itemsImported'])
        if epk_item:
            cleanup_published_items([epk_item])

    def test_group_import_to_same_gis_overwrite(self):
        """tests importing group items in same gis"""
        if not self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to same gis")

        res = self.import_group.migration.load(self.epk_item, overwrite=True)
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)
        if res.result()['itemsImported']:
            cleanup_published_items(res.result()['itemsImported'])

    def test_group_import_with_item_id(self):
        """tests importing multiple group items with item id specified"""
        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        epk_item = None
        res = None
        try:
            # epk item id for this test: 3752c8b4cd354e1eafcd32dbbf422af7
            epk_path = os.path.join(QALAB_ROOT_PATH, 'group_manager_data', 'samplesdata.epk')
            epk_item = add_source_item(
                self.to_gis, f"epk_{uuid.uuid4().hex[:4]}", ItemTypeEnum.EXPORT_PACKAGE, epk_path
            )
            import_group_content = self.import_group.migration.load(
                epk_item=epk_item,
                item_ids=["72224efc9e044001934bb3be87120beb"],
                overwrite=True,
                keep_epk_item=True,
            )
            res = import_group_content.result()
            assert "itemsSkipped" in res
            assert "itemsFailedImport" in res
        except Exception as e:
            raise e
        finally:
            if epk_item:
                cleanup_published_items([epk_item])
            if res['itemsImported']:
                cleanup_published_items(res['itemsImported'])

    def test_group_import_with_folder_id(self):
        """tests importing group items with specified folder id"""
        if self.from_gis.url == self.to_gis.url:
            self.skipTest("testing export and import to a different gis")

        if self.from_gis.version > self.to_gis.version:
            self.skipTest("The receiving Enterprise version must be the same or later of the exporting Enterprise.")

        # add epk item in destination gis group
        epk_item = add_source_item(
            self.to_gis, f"epk_{uuid.uuid4().hex[:4]}", ItemTypeEnum.EXPORT_PACKAGE, self.export_package_file
        )
        assert isinstance(epk_item, Item)

        # load item
        res = self.import_group.migration.load(epk_item=epk_item, folder_id="/")
        assert res
        assert isinstance(res, StatusJob)
        assert isinstance(res.result(), dict)
        if res.result()['itemsImported']:
            cleanup_published_items(res.result()['itemsImported'])
        if epk_item:
            cleanup_published_items([epk_item])

    @classmethod
    def tearDownClass(cls):
        """delete items, folders and groups"""
        if cls.item:
            cleanup_published_items([cls.item])
        if cls.epk_item:
            cleanup_published_items([cls.epk_item])
        cleanup_groups([cls.export_group, cls.import_group])
        cleanup_folders(cls.from_gis, ["imports_", "exports"])


if __name__ == "__main__":
    unittest.main()
