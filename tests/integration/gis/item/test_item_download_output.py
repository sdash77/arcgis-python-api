# -----------------------------------------------------------------------------
# Name:        Test for the output of the download method of the Item class.
#              Multiple item types, including empty items, are tested for the
#              location and format of outputs varying the use of the save_path
#              argument.
# Purpose:     Integration tests for downloading items using ArcGIS Python API.
# -----------------------------------------------------------------------------

import unittest
import time
import tempfile
from pathlib import Path

from integration.config import get_resource_path, INTEGRATION_TEST_ITEM_TAG
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    add_source_item,
    publish_test_item,
    cleanup_published_items,
    cleanup_folders,
)

from arcgis.gis import ItemTypeEnum, ItemProperties


def setUpModule():
    import warnings

    warnings.filterwarnings("ignore")


@profiles.admin_all
@integration_test
class Test_Item_download_outputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f"\n{'=' * 5} begin setUpClass {'=' * 20}")
        print(f"{' ' * 10}test class: {cls.__name__}")
        start = time.perf_counter()

        cls.item_test_download_folder = cls.gis.content.folders._get_or_create(
            "item_download_ntgrtn_tests"
        )

        # add csv item and publish point feature layer from it, then create
        # a map object, add layer to it and save as new web map item for testing
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
            folder=cls.item_test_download_folder,
        )

        cls.chicago_map = cls.gis.map("Chicago")
        cls.chicago_map.content.add(cls.chicago_wfl_item)
        cls.chi_webmap = cls.chicago_map.save(
            item_properties={
                "title": "chicago_webmap_downtest",
                "tags": INTEGRATION_TEST_ITEM_TAG,
                "snippet": "Web Map to test downloading",
            },
            folder=cls.item_test_download_folder.name,
        )

        cls.mmpk_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_mmpk_usa.mmpk",
            verify=True,
            unique_copy=True,
        )

        cls.mmpk_item = add_source_item(
            gis=cls.gis,
            layer_name="set1_mmpk_usa",
            item_type=ItemTypeEnum.MOBILE_MAP_PACKAGE,
            source_data_path=cls.mmpk_file,
            folder=cls.item_test_download_folder,
        )

        cls.png_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_shifting_opportunity.png",
            verify=True,
            unique_copy=True,
        )

        cls.img_item = add_source_item(
            gis=cls.gis,
            layer_name="image_for_download_testing",
            item_type=ItemTypeEnum.IMAGE,
            source_data_path=cls.png_file,
            folder=cls.item_test_download_folder,
        )

        cls.wmapp_item = cls.item_test_download_folder.add(
            item_properties=ItemProperties(
                title="empty_web_app_download_test",
                item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                snippet="Empty Web App item added with Folder in API.",
                description="Item of 0kb for Python API integration tests.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            )
        ).result()

        end = time.perf_counter()
        elapsed = end - start
        print(f"{' ' * 10}elapsed time: {elapsed/60:.2f} minutes.")
        print(f"{'=' * 5} end setUpClass {'=' * 20}\n")

    @classmethod
    def tearDownClass(cls):
        print(f"\n{'=' * 5} tear down: {cls.__name__}")
        test_items = list(cls.item_test_download_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(gis=cls.gis, folder_names=[cls.item_test_download_folder.name])
        print(f"{'=' * 5} end tearDownClass {'=' * 20}\n")

    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.perf_counter()

    def tearDown(self):
        elapsed_time = time.perf_counter() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time:.2f} seconds.\n")

    def test_download_method_empty_data_outpath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = self.chicago_wfl_item.download(save_path=temp_dir)
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on feature layer item with empty data resource throws error",
        )
        self.assertEqual(
            chicago_data_size, 0, "File size of feature layer download is > 0"
        )
        self.assertEqual(
            temp_dir,
            str(Path(chicago_data).parent),
            "Downloaded file not in tempory directory path as expected.",
        )

    ("for now")

    def test_download_method_empty_data_nopath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = self.chicago_wfl_item.download()
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on feature layer item with empty data resource throws error",
        )
        self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")
        self.assertEqual(
            Path(temp_dir).parent,
            Path(chicago_data).parent,
            "Download location with no path argument is not temporary directory path.",
        )

    ("for now")

    def test_download_method_txt_data_nopath(self):
        """
        When no path is provided, Item.download() downloads to sys temp dir
        """
        chicago_csv_item = self.chicago_wfl_item.related_items(
            "Service2Data", "forward"
        )[0]

        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_csv_item.download()
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsInstance(
            chicago_data,
            str,
            "Calling download() on csv item does not return download str path",
        )
        self.assertTrue(
            Path(chicago_data).stem.startswith("Chicago_points"),
            "Download file name does not match known csv file name.",
        )
        self.assertGreater(
            chicago_data_size, 0, "Downloaded file size is not greater than 0"
        )
        self.assertEqual(
            Path(temp_dir).parent,
            Path(chicago_data).parent,
            "Download of text data with no path does not return to temporary directory.",
        )

    def test_download_method_txt_data_outputpath(self):
        """
        When given a download path, ensure Item.download() downloads file into that path
        """
        chicago_csv_item = self.chicago_wfl_item.related_items(
            "Service2Data", "forward"
        )[0]

        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_csv_item.download(save_path=temp_dir)
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsInstance(
            chicago_data,
            str,
            "Calling download() on csv item does not return download str path",
        )
        self.assertTrue(
            Path(chicago_data).stem.startswith("Chicago_points"),
            "Download file name does not match known input",
        )

        self.assertEqual(
            str(Path(chicago_data).parent),
            str(temp_dir),
            "Download path does not match temporary directory path.",
        )

        self.assertGreater(
            chicago_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_Image_data_nopath(self):
        """
        For Image item, download with a path should return string representation of the item.
        :return:
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            img_download_data = self.img_item.download()
            img_size = Path(img_download_data).stat().st_size

        self.assertIsInstance(
            img_download_data,
            str,
            "Calling download() on Image item does not return download str path",
        )
        self.assertTrue(
            Path(img_download_data).name.endswith(".png"),
            "Download file name does not match known input",
        )
        self.assertIn(
            Path(self.png_file).stem,
            Path(img_download_data).stem,
            "Download file from Image item does not match known file name.",
        )
        self.assertGreater(img_size, 0, "Downloaded file size is not greater than 0")

    def test_download_method_Image_data_outpath(self):
        """
        For Image item, download with a path should return string representation of the item.
        :return:
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            img_download_data = self.img_item.download(save_path=temp_dir)
            img_size = Path(img_download_data).stat().st_size

        self.assertIsInstance(
            img_download_data,
            str,
            "Calling download() on Image item does not return download str path",
        )
        self.assertTrue(
            Path(img_download_data).name.endswith(".png"),
            "Download file name does not match known input",
        )
        self.assertIn(
            Path(self.png_file).stem,
            Path(img_download_data).stem,
            "Download file from Image item does not match known file name.",
        )
        self.assertGreater(img_size, 0, "Downloaded file size is not greater than 0")

    def test_download_method_zero_size_data(self):
        """
        When Item has no data or 0kb size - ensure Item.download() returns None
        :return:
        """
        wmapp_download_file = self.wmapp_item.download()
        wmapp_download_file_size = Path(wmapp_download_file).stat().st_size

        self.assertIsNotNone(
            wmapp_download_file, "Calling download() on zero kb item returns None"
        )
        self.assertEqual(wmapp_download_file_size, 0, "Downloaded file size is not 0")

    def test_download_method_JSON_data_outputpath(self):
        """
        When Item has JSON data, ensure Item.download() downloads file into that path instead
        of returning parsed dict.
        """

        JSON_item = self.chi_webmap

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = JSON_item.download(save_path=temp_dir)
            json_file_size = Path(json_file).stat().st_size

        self.assertIsInstance(
            json_file,
            str,
            "Calling download() on webmap item does not return download str path",
        )
        self.assertEqual(
            str(Path(json_file).parent),
            temp_dir,
            "Download file does not download to temporary directory.",
        )

        self.assertEqual(
            Path(json_file).stem,
            JSON_item.title,
            "Web Map download file name does not match title of web map item.",
        )
        self.assertGreater(
            json_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_JSON_data_nopath(self):
        """
        When Item has JSON data, ensure Item.download() downloads file into that path instead
        of returning parsed dict.
        """

        JSON_item = self.chi_webmap

        temp_dir = tempfile.TemporaryDirectory()
        json_file = JSON_item.download()
        json_file_size = Path(json_file).stat().st_size

        self.assertIsInstance(
            json_file,
            str,
            "Calling download() on webmap item does not return download str path",
        )
        self.assertEqual(
            Path(json_file).parent,
            Path(temp_dir.name).parent,
            "Download file does not download to temporary directory.",
        )

        self.assertIn(
            JSON_item.title,
            Path(json_file).stem,
            "Web Map download file name does not match title of web map item.",
        )
        self.assertGreater(
            json_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_binary_data_outputpath(self):
        """
        When Item has binary data - like layer packages, ensure Item.download() downloads file
        into that path instead of returning None or binary stream.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            map_pkg_file = self.mmpk_item.download(save_path=temp_dir)
            map_pkg_file_size = Path(map_pkg_file).stat().st_size

        self.assertIsInstance(
            map_pkg_file,
            str,
            "Calling download() on mmpk item does not return download str path",
        )
        self.assertEqual(
            str(Path(map_pkg_file).parent),
            temp_dir,
            "Download file location does not match known temporary directory.",
        )
        self.assertEqual(
            Path(map_pkg_file).suffix,
            ".mmpk",
            "Download file extension is not mmpk as expected",
        )
        self.assertIn(
            self.mmpk_item.title,
            Path(map_pkg_file).stem,
            "Download file name does not contain title of mmpk item.",
        )
        self.assertGreater(
            map_pkg_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_binary_data_nopath(self):
        """
        When Item has binary data - like layer packages, ensure Item.download() downloads file
        into that path instead of returning None or binary stream.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            map_pkg_file = self.mmpk_item.download()
            map_pkg_file_size = Path(map_pkg_file).stat().st_size

        self.assertIsInstance(
            map_pkg_file,
            str,
            "Calling download() on mmpk item does not return download str path",
        )
        self.assertEqual(
            Path(map_pkg_file).parent,
            Path(temp_dir).parent,
            "Download file location does not match known temporary directory parent.",
        )
        self.assertEqual(
            Path(map_pkg_file).suffix,
            ".mmpk",
            "Download file extension is not mmpk as expected",
        )
        self.assertIn(
            self.mmpk_item.title,
            Path(map_pkg_file).stem,
            "Download file name does not match title of mmpk item.",
        )
        self.assertGreater(
            map_pkg_file_size, 0, "Downloaded file size is not greater than 0"
        )


if __name__ == "__main__":
    unittest.main()
