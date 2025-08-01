# -----------------------------------------------------------------------------
# Name:        Test for the output of the get_data method of the Item class. 
#              Multiple item types, including empty items, are tested for the
#              location and format of outputs varying the use of the try_json
#              argument.
# Purpose:     Integration tests for getting data on items using Python API.
# -----------------------------------------------------------------------------

import unittest
import time
import tempfile
from pathlib import Path

from integration.config import (
    get_resource_path,
    INTEGRATION_TEST_ITEM_TAG
)
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    add_source_item,
    publish_test_item,
    cleanup_published_items,
    cleanup_folders
)

from arcgis.gis import ItemProperties, ItemTypeEnum

@profiles.admin_all
@integration_test
class Test_Item_get_data_outputs(unittest.TestCase):  
    @classmethod
    def setUpClass(cls):
        
        cls.item_test_get_data_folder = cls.gis.content.folders._get_or_create(
           "item_get_data_ntgrtn_tests"
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
            folder=cls.item_test_get_data_folder,
        )

        cls.chicago_map = cls.gis.map("Chicago")
        cls.chicago_map.content.add(cls.chicago_wfl_item)
        cls.chi_webmap = cls.chicago_map.save(
            item_properties={
                "title": "chicago_webmap_downtest",
                "tags": INTEGRATION_TEST_ITEM_TAG,
                "snippet": "Web Map to test downloading",
            },
            folder=cls.item_test_get_data_folder.name,
        )        
        
        cls.png_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_shifting_opportunity.png",
            verify=True,
            unique_copy=True,
        )
        cls.img_item = add_source_item(
            gis=cls.gis,
            layer_name="set1_shifting_opportunity",
            item_type=ItemTypeEnum.IMAGE,
            source_data_path=cls.png_file,
            folder=cls.item_test_get_data_folder,
        )
        
        cls.wmapp_item = cls.item_test_get_data_folder.add(
            item_properties=ItemProperties(
                title="set1_empty_webapp_api",
                item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                snippet="Empty Web App item added with Folder in API.",
                description="Item of 0kb for Python API integration tests.", 
                tags=INTEGRATION_TEST_ITEM_TAG
            )
        ).result()
        
        cls.word_file_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/summary_temp.docx",
                verify=True,
                unique_copy=True,
            )
        
        cls.word_item = add_source_item(
            gis=cls.gis,
            layer_name="xsummary_temp",
            item_type=ItemTypeEnum.MICROSOFT_WORD,
            source_data_path=cls.word_file_path,
            folder=cls.item_test_get_data_folder
        )
        
    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")
        test_items = list(cls.item_test_get_data_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(
            gis=cls.gis,
            folder_names=[cls.item_test_get_data_folder.name]
        )         
    
    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.time()
        
    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time / 60:.2f} minutes.\n")
        
    def test_get_data_method_Image(self):
        """
        For Image item, item.get_data(False) should return string representation of the item.
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
            self.img_item.title,
            Path(img_download_data).stem,
            "Download file from Image item does not match known file name."
        )
        self.assertGreater(
            img_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_zero_size_data(self):
        """
        When Item has no data or 0kb size - ensure Item.download() returns None
        :return:
        """      
        
        wmapp_download_file = self.wmapp_item.download()
        wmapp_download_file_size = Path(wmapp_download_file).stat().st_size
        
        self.assertIsNotNone(
            wmapp_download_file,
            "Calling download() on zero kb item returns None"
        )
        self.assertEqual(
            wmapp_download_file_size,
            0,
            "Downloaded file size is not 0"
        )

    def test_get_data_method_binary_data_tryjson_True(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path even if try_json is set to True
        """

        item_data = self.word_item.get_data(try_json=True)
        item_data_size = Path(item_data).stat().st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on lpk item does not return download str path",
        )
        self.assertEqual(
            str(Path(item_data).parent),
            str(tempfile.gettempdir()),
            "Download file location does not match temporary directory."
        )
        self.assertTrue(
            Path(item_data).name.endswith(".docx"),
            "Download of Word item did not produce correct file extension."
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_binary_data_tryjson_False(self):
        """
        When Item has binary data - like layer packages, word docs, etc. ensure 
        Item.get_data() downloads file into a path when try_json is set to False.
        """
        
        item_data = self.word_item.get_data(try_json=False)
        item_data_size = Path(item_data).stat().st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on map doc item does not return download str path",
        )
        self.assertEqual(
            str(Path(item_data).parent),
            str(tempfile.gettempdir()),
            "Download file location does not match temporary directory."
        )
        self.assertTrue(
            Path(item_data).name.endswith(".docx"),
            "Download of Word item did not produce correct file extension."
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_JSON_data_tryjson_False(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json False,
        should return the data as str instead of dict.
        :return:
        """

        webmap_item = self.chi_webmap
        item_data = webmap_item.get_data(try_json=False)

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on web map item does not return data as str with try_json is false",
        )
        self.assertTrue(
            "baseMapLayers" in item_data,
            "JSON string of web map does not have baseMapLayers as expected."
        )

    def test_get_data_method_JSON_data_tryjson_True(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json True,
        should return the data dict instead of str.
        """
        
        webmap_item = self.chi_webmap
        item_data = webmap_item.get_data(try_json=True)

        self.assertIsInstance(
            item_data,
            dict,
            "Calling get_data() on web map item does not return data as dict with try_json is true",
        )
        self.assertTrue(
            "baseMap" in list(item_data.keys()),
            "Web Map JSON does not contain a baseMap as required."
        )

    def test_get_data_method_zero_size_data_tryjson_False(self):
        """
        When Item has no data, calling Item.get_data() with try_json False,
        should return None.
        """
        
        wmapp_item = self.wmapp_item
        wmapp_data = wmapp_item.get_data(try_json=False)

        self.assertIsNone(
            wmapp_data,
            "Calling get_data() on empty item with tryjson False does not return None",
        )

    def test_get_data_method_zero_size_data_tryjson_True(self):
        """
        When Item has no data, calling Item.get_data() with try_json True,
        should return empty dict.
        :return:
        """
       
        wmapp_item = self.wmapp_item
        item_data = wmapp_item.get_data(try_json=True)

        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on empty item with tryjson False does not return an empty dictionary.",
        )

    def test_get_data_method_empty_data_tryjson_True(self):
        """
        When Item has no data, but item.size > 0, calling Item.get_data() with try_json True,
        should return an empty dict.
        """
        
        item = self.chicago_wfl_item
        if not item:
            self.skipTest("Feature Layer item not published as part of setUpClass as expected.")
        
        self.assertGreater(
            item.size,
            0,
            "Invalid item for this testcase, its size is not greater than 0",
        )

        item_data = item.get_data(try_json=True)

        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on item with no data and tryjson False does not return empty dict.",
        )
        
    def test_get_data_method_empty_data_tryjson_False(self):
        """
        When Item has no data, but item.size > 0, calling Item.get_data() with try_json True,
        should return an empty dict.
        """
        
        item = self.chicago_wfl_item
        if not item:
            self.skipTest("Feature Layer item not published as part of setUpClass as expected.")
        
        self.assertGreater(
            item.size,
            0,
            "Invalid item for this testcase, its size is not greater than 0",
        )

        item_data = item.get_data(try_json=False)

        self.assertIsNone(
            item_data,
            "Calling get_data() on item with no data and tryjson False does not None.",
        )
        
if __name__ == "__main__":
    unittest.main()