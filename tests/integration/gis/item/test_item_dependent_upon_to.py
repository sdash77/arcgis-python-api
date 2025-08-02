# -------------------------------------------------------------------------------
# Name:        Test for the dependent_to and dependent_upon methods  of the Item
#              class in Enterprise and Kubernetes. Methods not supported in
#              Online. Various item types are verified for return values and
#              types.
# Purpose:     Integration tests for dependency methods using ArcGIS Python API.
# -------------------------------------------------------------------------------

import unittest
import time

from integration.config import get_resource_path, INTEGRATION_TEST_ITEM_TAG
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items, cleanup_folders

from arcgis.gis import ItemTypeEnum, GIS


def setUpModule():
    import warnings

    warnings.filterwarnings("ignore")


@profiles.admin_enterprise_and_k8s
@integration_test
class Test_Item_dependent_methods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n======= begin setUpClass ====================================\n")

        cls.item_test_depend_folder = cls.gis.content.folders._get_or_create(
            "item_depend_ntgrtn_tests"
        )

        cls.chicago_source_data = get_resource_path(
            relative_path="staging_data/item_class_test_data/Chicago_points.csv",
            verify=True,
            unique_copy=True,
        )
        cls.chicago_wfl_item = publish_test_item(
            gis=cls.gis,
            layer_name="Chicago_test_points",
            item_type=ItemTypeEnum.CSV,
            source_data_path=cls.chicago_source_data,
            prep_for_editing=False,
            folder=cls.item_test_depend_folder,
        )

        cls.chicago_map = cls.gis.map("Chicago")
        cls.chicago_map.content.add(cls.chicago_wfl_item)
        cls.chi_webmap = cls.chicago_map.save(
            item_properties={
                "title": "chicago_webmap_downtest",
                "tags": INTEGRATION_TEST_ITEM_TAG,
                "snippet": "Web Map to test downloading",
            },
            folder=cls.item_test_depend_folder.name,
        )

        print("\n======= end setUpClass ==========================================\n")

    @classmethod
    def tearDownClass(cls):
        print("\n======= begin tearDownClass =================================\n")
        test_items = list(cls.item_test_depend_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(gis=cls.gis, folder_names=[cls.item_test_depend_folder.name])
        print("\n======= end tearDownClass ====================================")

    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.time()

    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time / 60:.2f} minutes.\n")

    def test_dependencies_hfs(self):
        """Test output for dependencies of a Hosted Feature Layer item."""

        # get a hosted Feature Layer item
        flyr_item = self.chicago_wfl_item

        fl_dep_upon = flyr_item.dependent_upon()
        fl_dep_to = flyr_item.dependent_to()

        self.assertIsInstance(
            fl_dep_upon, dict, "The dependent_upon method did not return a dictionary."
        )
        self.assertGreaterEqual(
            len(fl_dep_upon["list"]),
            1,
            "Hosted feature layer always dependent on at least hosting server.",
        )
        self.assertGreater(
            len(fl_dep_to["list"]),
            0,
            "Hosted feature layer is a dependency of a Web Map.",
        )

    def test_dependencies_webmap(self):
        """Test output for dependencies of a Web Map item."""
        wm_item = self.chi_webmap

        wm_dep_upon = wm_item.dependent_upon()
        wm_dep_to = wm_item.dependent_to()

        # assert webmap dependency
        self.assertIsNotNone(
            wm_dep_upon, "Web Map item always dependent upon url item."
        )
        self.assertGreaterEqual(
            len(wm_dep_upon["list"]),
            1,
            "Web Map always dependent_upon at least a basemap url",
        )
        self.assertEqual(
            len(wm_dep_to["list"]),
            0,
            "No item is dependent upon this Web Map to exist.",
        )

    def test_dependencies_csv(self):
        """Test output for dependencies of a CSV item."""

        csv_item = self.chicago_wfl_item.related_items("Service2Data", "forward")[0]

        csv_dep_upon = csv_item.dependent_upon()
        csv_dep_to = csv_item.dependent_to()

        # assert csv item dependency none
        self.assertIsInstance(
            csv_dep_upon, dict, "The dependent upon method did not return a dict."
        )
        self.assertEqual(
            csv_dep_upon["total"],
            0,
            "A default CSV item should have 0 dependencies",
        )


if __name__ == "__main__":
    unittest.main()
