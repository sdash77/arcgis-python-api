# -------------------------------------------------------------------------------
# Name:        Item class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import os
import uuid

from integration.dino_utils.dino_configs import DinoConfigs
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test

from configparser import ConfigParser
import datetime
import tempfile
from pandas import read_csv

# region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if r1 & r2:
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise (exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
    from arcgis import features
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check


# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module Item class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


@integration_test
class Test_Item_portal_builtin(unittest.TestCase):
    """
    Test to check if a Item object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """
        cls.gis = GIS(
            profile="your_ent_admin_profile",
            verify_cert=False,
        )
        if cls.gis is None:
            cls.class_skip = True

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_data_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_dataprep"]
        )
        cls.qalab_cls_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_Item_cls"]
        )

        # region publish necessary web layers
        # upload csv item
        cls.one_to_many_csv_item = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv", "csv"
        )
        if not cls.one_to_many_csv_item:
            csv_path = os.path.join(
                cls.qalab_cls_path, "set1_overwrite_manyHFS_csv.csv"
            )
            cls.one_to_many_csv_item = cls.gis.content.add({}, data=csv_path)
            print("CSV item added")
            cls.assertIsNotNone(cls.one_to_many_csv_item, "Cannot add csv item")

        # publish the csv item - 1
        cls.one_to_many_wfl_item_1 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_1", "Feature Service"
        )
        if not cls.one_to_many_wfl_item_1:
            csv_path_1 = os.path.join(
                cls.qalab_cls_path, "set1_overwrite_manyHFS_csv_1.csv"
            )
            cls.one_to_many_csv_item_1 = cls.gis.content.add({}, data=csv_path_1)
            print("CSV_1 item added")
            cls.one_to_many_wfl_item_1 = cls.one_to_many_csv_item_1.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_1"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_1, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_1")
            cls.one_to_many_wfl_item_1.update({"title": "set1_overwrite_manyHFS_csv_1"})

        # publish the csv item - 2
        cls.one_to_many_wfl_item_2 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_2", "Feature Service"
        )
        if not cls.one_to_many_wfl_item_2:
            csv_path_2 = os.path.join(
                cls.qalab_cls_path, "set1_overwrite_manyHFS_csv_2.csv"
            )
            cls.one_to_many_csv_item_2 = cls.gis.content.add({}, data=csv_path_2)
            print("CSV_2 item added")
            cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item_2.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_2"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_2, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_2")
            cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})

        # publish csv item 2 for overwrite
        cls.one_to_one_csv_item = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_HFS_csv2", "CSV"
        )
        if not cls.one_to_one_csv_item:
            csv_path = os.path.join(cls.qalab_cls_path, "set1_overwrite_HFS_csv2.csv")
            cls.one_to_one_csv_item = cls.gis.content.add({}, data=csv_path)
            print("CSV item added for one to one overwrite case")
            cls.assertIsNotNone(
                cls.one_to_one_csv_item, "Cannot add csv item for one to one case"
            )

        cls.one_to_one_wfl_item = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_HFS_csv2", "Feature Layer"
        )
        if not cls.one_to_one_wfl_item:
            cls.one_to_one_wfl_item = cls.one_to_one_csv_item.publish()
            print("CSV item published for one to one overwrite case")
            cls.assertIsNotNone(
                cls.one_to_one_wfl_item, "Cannot publish csv item for one to one case"
            )
        # endregion

        # region print banner
        print("==================================================================")
        print("Beginning tests in Test_Item_portal_builtin class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_Item_"

        # region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(
            self.gis, self.test_case_name, None
        )

        if search_result is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, search_result)
            if not delete_result[0]:
                test_skip = True  # cannot run test case if old output is not deleted
                print("Failed to delete old test output: " + str(delete_result[1]))
            else:
                print("setUp : deleted old output. Proceeding to test case")
        else:
            print("setUp: not old outputs found. Proceeding to test case")
        # endregion

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_vtpk(self):
        vtpk_package_name = "set2_vtpk_worldgreen.vtpk"

        # region delete old service on portal
        service_title = os.path.splitext(vtpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Vector Tile Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for vtpk item
            sr = self.gis.content.search(
                vtpk_package_name, item_type="Vector Tile Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                vtpk_item = sr[0]
                print("Old VTPK item found and will be used")

            else:
                print("Old VTPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", vtpk_package_name
                )
                vtpk_item = self.gis.content.add(
                    {"type": "Vector Tile Package"}, file_path
                )

            # publish vtpk item
            publish_output = vtpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish VTPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Vector Tile Service",
                    "Publishing VPTK does not create an item "
                    "of type Vector Tile Service",
                )

                # validate service item has layers
                self.assertTrue(
                    len(publish_output.layers) > 0,
                    "No layers found in Vector Tile Service",
                )
                print("Passed: VTPK successfully published as VTS")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_spk(self):
        spk_package_name = "set2_spk_SD3dbuildings.spk"

        # region delete old service on portal
        service_title = os.path.splitext(spk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Scene Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                spk_package_name, item_type="Scene Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                spk_item = sr[0]
                print("Old SPK item found and will be used")

            else:
                print("Old SPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", spk_package_name
                )
                spk_item = self.gis.content.add({"type": "Scene Package"}, file_path)

            # publish vtpk item
            publish_output = spk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish SPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Scene Service",
                    "Publishing SPK does not create an item " "of type Scene Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Scene Service")
                print("Passed: SPK successfully published as WSL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_tpk(self):
        tpk_package_name = "set2_tpk_SD.tpk"

        # region delete old service on portal
        service_title = os.path.splitext(tpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, "Map Service")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                tpk_package_name, item_type="Tile Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                tpk_item = sr[0]
                print("Old TPK item found and will be used")

            else:
                print("Old TPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", tpk_package_name
                )
                tpk_item = self.gis.content.add({"type": "Tile Package"}, file_path)

            # publish tpk item
            publish_output = tpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish TPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Map Service",
                    "Publishing TPK does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: TPK successfully published as WTL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_shp(self):
        zip_package_name = "set1_line.zip"

        # region delete old service on portal
        service_title = os.path.splitext(zip_package_name)[0]
        for service_type in ["Feature Service", "Map Service"]:
            old_sr = PortalUtils.search_portal_item(
                self.gis, service_title, service_type
            )
            if old_sr is not None:
                delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
                if not delete_result:
                    self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                zip_package_name, item_type="Shapefile", max_items=1
            )
            if sr is not None and len(sr) > 0:
                zip_item = sr[0]
                print("Old Zipped item found and will be used")

            else:
                print("Old zip not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "shp", zip_package_name)
                zip_item = self.gis.content.add({"type": "Shapefile"}, file_path)

            # publish tpk item
            publish_output = zip_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish ZIP item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Feature Service",
                    "Publishing SHP does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: Shapefile successfully published as WTL")

            tile_item = publish_output.create_tile_service(
                "Streets_Centerline", 1500000, 40000
            )
            print(tile_item)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_resources_property(self):
        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }
        try:
            added_item = self.gis.content.add(item_properties_dict)
            if added_item is not None:
                print("Vector tile service item created")

        except:
            print("Unable to create a new item to test adding resources")
            raise unittest.SkipTest

        # get resources property of this item
        try:
            res_mgr = added_item.resources

            self.assertIsInstance(
                res_mgr,
                arcgis.gis.ResourceManager,
                "item.resources does not return"
                "an object of type arcgis.gis.ResourceManager. "
                "Instead returns " + str(type(res_mgr)),
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_empty_data(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_wfl_item.download(save_path=temp_dir)
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsNotNone(
                chicago_data,
                "Calling download() on Item with empty resource throws error",
            )
            self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_empty_data_nopath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_wfl_item.download()
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsNotNone(
                chicago_data,
                "Calling download() on Item with empty resource throws error",
            )
            self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_txt_data_nopath(self):
        """
        When no path is provided, Item.download() downloads to sys temp dir
        :return:
        """
        try:
            chicago_csv_item = self.gis.content.search("set1_Chicago", "CSV")[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_csv_item.download()
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsInstance(
                chicago_data,
                str,
                "Calling download() on csv item does not return download str path",
            )
            self.assertTrue(
                chicago_data.endswith("set1_Chicago.csv"),
                "Download file name does not match known input",
            )
            self.assertGreater(
                chicago_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_txt_data_outputpath(self):
        """
        When given a download path, ensure Item.download() downloads file into that path
        :return:
        """
        try:
            chicago_csv_item = self.gis.content.search("set1_Chicago", "CSV")[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_csv_item.download(save_path=temp_dir)
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsInstance(
                chicago_data,
                str,
                "Calling download() on csv item does not return download str path",
            )
            self.assertTrue(
                chicago_data.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                chicago_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_JSON_data_outputpath(self):
        """
        When Item has JSON data, ensure Item.download() downloads file into that path instead
        of returning parsed dict
        :return:
        """
        try:
            JSON_item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                json_file = JSON_item.download(save_path=temp_dir)
                json_file_size = os.stat(json_file).st_size

            self.assertIsInstance(
                json_file,
                str,
                "Calling download() on webmap item does not return download str path",
            )
            self.assertTrue(
                json_file.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                json_file_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_binary_data_outputpath(self):
        """
        When Item has binary data - like layer packages, ensure Item.download() downloads file
        into that path instead of returning None or binary stream.
        :return:
        """
        try:
            JSON_item = self.gis.content.search("set1_mmpk_usa", "Mobile Map Package")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                json_file = JSON_item.download(save_path=temp_dir)
                json_file_size = os.stat(json_file).st_size

            self.assertIsInstance(
                json_file,
                str,
                "Calling download() on mmpk item does not return download str path",
            )
            self.assertTrue(
                json_file.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                json_file_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_Image(self):
        """
        For Image item, item.get_data(False) should return string representation of the item.
        :return:
        """
        try:
            data_item = self.gis.content.search(
                "set1_shifting_opportunity.png", "Image"
            )[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                item_data = data_item.download()
                data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling download() on Image item does not return download str path",
            )
            self.assertTrue(
                item_data.endswith(".png"),
                "Download file name does not match known input",
            )
            self.assertGreater(
                data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_zero_size_data(self):
        """
        When Item has no data or 0kb size - ensure Item.download() returns None
        :return:
        """
        try:
            JSON_item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            json_file = JSON_item.download()
            json_file_size = os.stat(json_file).st_size
            self.assertIsNotNone(
                json_file, "Calling download() on zero kb item returns None"
            )
            self.assertEqual(json_file_size, 0, "Downloaded file size is not 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_binary_data_tryjson_True(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path even if try_json is set to True
        :return:
        """
        try:
            item = self.gis.content.search("set1_lpk", "Layer Package")[0]
            item_data = item.get_data(try_json=True)
            item_data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on lpk item does not return download str path",
            )
            self.assertTrue(
                item_data.startswith(str(tempfile.gettempdir())),
                "Download file name does not match known input",
            )
            self.assertGreater(
                item_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_binary_data_tryjson_False(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path when try_json is set to False
        :return:
        """
        try:
            item = self.gis.content.search("set1_geometric", "Map Document")[0]
            item_data = item.get_data(try_json=False)
            item_data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on map doc item does not return download str path",
            )
            self.assertTrue(
                item_data.startswith(str(tempfile.gettempdir())),
                "Download file name does not match known input",
            )
            self.assertGreater(
                item_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_JSON_data_tryjson_False(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json False,
        should return the data as str instead of dict
        :return:
        """
        try:
            item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            item_data = item.get_data(try_json=False)

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on web map item does not return data as str with try_json is false",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_JSON_data_tryjson_True(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json True,
        should return the data dict instead of str
        :return:
        """
        try:
            item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            item_data = item.get_data(try_json=True)

            self.assertIsInstance(
                item_data,
                dict,
                "Calling get_data() on web map item does not return data as dict with try_json is true",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_zero_size_data_tryjson_False(self):
        """
        When Item has no data, calling Item.get_data() with try_json False,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            item_data = item.get_data(try_json=False)

            self.assertIsNone(
                item_data,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_zero_size_data_tryjson_True(self):
        """
        When Item has no data, calling Item.get_data() with try_json True,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            item_data = item.get_data(try_json=True)

            self.assertEqual(
                len(item_data),
                0,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_empty_data_tryjson_True(self):
        """
        When Item has no data, but item.size > 0, calling Item.get_data() with try_json True,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.search("set1_Chicago", "Feature Layer")[0]
            self.assertGreater(
                item.size,
                0,
                "Invalid item for this testcase, its size is not greater than 0",
            )

            item_data = item.get_data(try_json=True)

            self.assertEqual(
                len(item_data),
                0,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_overwrite_item(self):
        """
        Update a csv item with new csv file. Ensure the contents are updated and
        itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(self.gis, "set1_overwrite_old", "CSV")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
        # endregion

        try:
            # upload csv item
            csv_path = os.path.join(self.qalab_cls_path, "set1_overwrite_old.csv")
            csv_item = self.gis.content.add({}, data=csv_path)

            self.assertIsNotNone(csv_item, "Cannot add csv item")
            old_item_id = csv_item.id

            # update csv item
            new_csv_path = os.path.join(self.qalab_cls_path, "set1_overwrite_new.csv")
            item_update_result = csv_item.update({}, data=new_csv_path)
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )
            new_item_id = csv_item.id

            self.assertEqual(
                old_item_id, new_item_id, "Item ID is not same after overwriting"
            )

            # verify content is updated
            csv_download_path = csv_item.download()

            # read contents
            new_df = read_csv(new_csv_path)
            downloaded_file_df = read_csv(csv_download_path)
            self.assertEqual(
                new_df.shape,
                downloaded_file_df.shape,
                "The number of rows cols of csv item not same as updated csv file",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_overwrite_manyHFS_using_csv_errors(self):
        """
        Multiple feature layers are published using a csv. Trying to overwrite this should raise RunTime Error
        :return:
        """

        try:
            # update csv item
            new_csv_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_manyHFS_csv.csv"
            )
            item_update_result = self.one_to_many_csv_item.update({}, data=new_csv_path)
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )
            print("CSV item updated")

            # overwrite the feature layer
            with self.assertRaises(RuntimeError) as expectedException:
                overwrite_result = self.one_to_many_csv_item.publish(overwrite=True)
            self.assertTrue(
                "User cant overwrite this service, using this data"
                in str(expectedException.exception)
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Duplicate test, turn off for speed")
    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region delete_features in old service on portal
        wfl_item = self.one_to_one_wfl_item
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Cannot delete old features")

        # get number of features after deleting all features. should be 0
        num_features_after_delete = flayer.query(return_count_only=True)
        # endregion

        try:
            # upload csv item - for update
            csv_item = self.one_to_one_csv_item
            new_csv_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_csv2.csv"
            )
            item_update_result = csv_item.update({}, data=new_csv_path)
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = csv_item.publish(overwrite=True)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # assert item id of feature layer is same
            self.assertEqual(
                overwrite_result.id,
                wfl_item.id,
                "Item ID is not same after overwriting",
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite,
                num_features_after_delete,
                "Overwrite did not add new features",
            )

            # verify num of features and attributes is as expected
            flayer = overwrite_result.layers[0]
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer not same as new csv",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(True, "Duplicate test, turn off for speed")
    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region find wfl is present, else publish it.
        fgdb_item = PortalUtils.search_portal_item(
            self.gis, "title:set1_Item_overwrite_HFS_fgdb.gdb", "File Geodatabase"
        )
        if fgdb_item is None:
            fgdb_path = os.path.join(
                self.qalab_cls_path, "set1_Item_overwrite_HFS_fgdb.gdb.zip"
            )
            fgdb_item = self.gis.content.add({}, data=fgdb_path)
            self.assertIsNotNone(fgdb_item, "Cannot add fgdb item")

        wfl_item = PortalUtils.search_portal_item(
            self.gis, "set1_Item_overwrite_HFS_fgdb", "Feature Service"
        )
        if wfl_item is None:
            wfl_item = fgdb_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish fgdb into a feature service")
        # endregion

        # delete all features from the feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(
            num_features_after_delete, 0, "Delete_features did not remove all features."
        )
        # endregion

        try:
            # update fdgb item
            new_fgdb_path = os.path.join(
                self.qalab_cls_path,
                "overwrite_wfl",
                "set1_Item_overwrite_HFS_fgdb.gdb.zip",
            )
            item_update_result = fgdb_item.update({}, data=new_fgdb_path)
            self.assertTrue(
                item_update_result, "Calling update on fgdb item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = fgdb_item.publish(overwrite=True)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                wfl_item.id, new_wfl_item_id, "Item ID is not same after overwriting"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "OVerwrite failed to add new features."
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_dependent_upon_ownItems(self):
        """
        As an item owner, I should be able to get my Item's dependencies
        :return:
        """

        # get an item
        chicago_csv_item = self.gis.content.search("set1_Chicago", "CSV")[0]
        wm = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
        try:
            chicago_deps = chicago_csv_item.dependent_upon()
            wm_deps = wm.dependent_upon()

            # assert csv item dependency none
            self.assertIsNotNone(
                chicago_deps, "Unable to get dependencies for CSV item"
            )
            self.assertEqual(
                chicago_deps["total"],
                0,
                "A default CSV item should have 0 dependencies",
            )

            # assert webmap dependency
            self.assertIsNotNone(
                wm_deps, "Unable to get dependencies for a webmap item"
            )
            self.assertGreaterEqual(
                len(wm_deps["list"]),
                2,
                "at least 1 dependency should be found for cities webmap",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


@integration_test
class Test_Item_arcgis_online(unittest.TestCase):
    """
    Test to check if a Item object works with ArcGIS Online org
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal can be reached
        Get class test asset location
        :return:
        """
        cls.gis = GIS(profile="your_online_admin_profile", verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True
        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_data_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_dataprep"]
        )
        cls.qalab_cls_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_Item_cls"]
        )

        # region publish necessary web layers
        cls.one_to_many_csv_item = cls.gis.content.search(
            f"title:set1_overwrite_manyHFS_csv AND owner:{cls.gis.users.me.username}",
            "CSV",
        )
        if not cls.one_to_many_csv_item:
            # upload csv item
            csv_path = os.path.join(cls.qalab_cls_path, "set1_overwrite_manyHFS_csv")
            cls.one_to_many_csv_item = cls.gis.content.add({}, data=csv_path)
            print("CSV item added")
            cls.assertIsNotNone(cls.one_to_many_csv_item, "Cannot add csv item")

        cls.one_to_many_wfl_item_1 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_1", "Feature Layer"
        )
        if not cls.one_to_many_wfl_item_1:
            # publish the csv item - 1
            cls.one_to_many_wfl_item_1 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_1"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_1, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_1")
            cls.one_to_many_wfl_item_1.update({"title": "set1_overwrite_manyHFS_csv_1"})

        cls.one_to_many_wfl_item_2 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_2", "Feature Layer"
        )
        if not cls.one_to_many_wfl_item_2:
            # publish the csv item - 2
            cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_2"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_2, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_2")
            cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})
        # endregion

        # region print banner
        print("==================================================================")
        print("Beginning tests in Test_Item_portal_builtin class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_Item_"

        # region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(
            self.gis, self.test_case_name, None
        )

        if search_result is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, search_result)
            if not delete_result[0]:
                test_skip = True  # cannot run test case if old output is not deleted
                print("Failed to delete old test output: " + str(delete_result[1]))
            else:
                print("setUp : deleted old output. Proceeding to test case")
        else:
            print("setUp: not old outputs found. Proceeding to test case")
        # endregion

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_vtpk(self):
        vtpk_package_name = "set2_vtpk_worldgreen.vtpk"

        # region delete old service on portal
        service_title = os.path.splitext(vtpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Vector Tile Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for vtpk item
            sr = self.gis.content.search(
                f"title:{vtpk_package_name}",
                item_type="Vector Tile Package",
                max_items=1,
            )
            if sr is not None and len(sr) > 0:
                vtpk_item = sr[0]
                print("Old VTPK item found and will be used")

            else:
                print("Old VTPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", vtpk_package_name
                )
                vtpk_item = self.gis.content.add(
                    {"type": "Vector Tile Package"}, file_path
                )

            # publish vtpk item
            publish_output = vtpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish VTPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Vector Tile Service",
                    "Publishing VPTK does not create an item "
                    "of type Vector Tile Service",
                )

                # validate service item has layers
                self.assertTrue(
                    len(publish_output.layers) > 0,
                    "No layers found in Vector Tile Service",
                )
                print("Passed: VTPK successfully published as VTS")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_spk(self):
        spk_package_name = "set2_spk_SD3dbuildings.spk"

        # region delete old service on portal
        service_title = os.path.splitext(spk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Scene Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                spk_package_name, item_type="Scene Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                spk_item = sr[0]
                print("Old SPK item found and will be used")

            else:
                print("Old SPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", spk_package_name
                )
                spk_item = self.gis.content.add({"type": "Scene Package"}, file_path)

            # publish vtpk item
            publish_output = spk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish SPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Scene Service",
                    "Publishing SPK does not create an item " "of type Scene Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Scene Service")
                print("Passed: SPK successfully published as WSL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_tpk(self):
        tpk_package_name = "set2_tpk_SD.tpk"

        # region delete old service on portal
        service_title = os.path.splitext(tpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, "Map Service")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                tpk_package_name, item_type="Tile Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                tpk_item = sr[0]
                print("Old TPK item found and will be used")

            else:
                print("Old TPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", tpk_package_name
                )
                tpk_item = self.gis.content.add({"type": "Tile Package"}, file_path)

            # publish tpk item
            publish_output = tpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish TPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Map Service",
                    "Publishing TPK does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: TPK successfully published as WTL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_publish_sd(self):
        sd_name = "NewPy_WTL_test_SingleLayerBuildCache.sd"

        # region delete old service on portal
        service_title = os.path.splitext(sd_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, "Map Service")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                sd_name, item_type="Service Definition", max_items=1
            )
            if sr is not None and len(sr) > 0:
                sd_item = sr[0]
                print("Old SD item found and will be used")

            else:
                print("Old SD not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "SDs", sd_name)
                sd_item = self.gis.content.add(
                    {"type": "Service Definition"}, file_path
                )

            # publish sd item
            publish_output = sd_item.publish(build_initial_cache=True)

            # validate
            if publish_output is None:
                self.fail("Failed to publish SD item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Map Service",
                    "Publishing SD does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                self.assertTrue(
                    len(publish_output.layers) > 0, "No layers found in Map Service"
                )
                print("Passed: SD successfully published as WTL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_resources_property(self):
        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }
        try:
            added_item = self.gis.content.add(item_properties_dict)
            if added_item is not None:
                print("Vector tile service item created")

        except:
            print("Unable to create a new item to test adding resources")
            raise unittest.SkipTest

        # get resources property of this item
        try:
            res_mgr = added_item.resources

            self.assertIsInstance(
                res_mgr,
                arcgis.gis.ResourceManager,
                "item.resources does not return"
                "an object of type arcgis.gis.ResourceManager. "
                "Instead returns " + str(type(res_mgr)),
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_empty_data(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_wfl_item.download(save_path=temp_dir)
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsNotNone(
                chicago_data,
                "Calling download() on Item with empty resource throws error",
            )
            self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_empty_data_nopath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_wfl_item.download()
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsNotNone(
                chicago_data,
                "Calling download() on Item with empty resource throws error",
            )
            self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_txt_data_nopath(self):
        """
        When no path is provided, Item.download() downloads to sys temp dir
        :return:
        """
        try:
            chicago_csv_item = self.gis.content.get("88048ba287c844928d1bf4b98dfe72f0")
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_csv_item.download()
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsInstance(
                chicago_data,
                str,
                "Calling download() on csv item does not return download str path",
            )
            self.assertTrue(
                chicago_data.endswith("set1_Chicago.csv"),
                "Download file name does not match known input",
            )
            self.assertGreater(
                chicago_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_txt_data_outputpath(self):
        """
        When given a download path, ensure Item.download() downloads file into that path
        :return:
        """
        try:
            chicago_csv_item = self.gis.content.search("set1_Chicago", "CSV")[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                chicago_data = chicago_csv_item.download(save_path=temp_dir)
                chicago_data_size = os.stat(chicago_data).st_size

            self.assertIsInstance(
                chicago_data,
                str,
                "Calling download() on csv item does not return download str path",
            )
            self.assertTrue(
                chicago_data.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                chicago_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_JSON_data_outputpath(self):
        """
        When Item has JSON data, ensure Item.download() downloads file into that path instead
        of returning parsed dict
        :return:
        """
        try:
            JSON_item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                json_file = JSON_item.download(save_path=temp_dir)
                json_file_size = os.stat(json_file).st_size

            self.assertIsInstance(
                json_file,
                str,
                "Calling download() on webmap item does not return download str path",
            )
            self.assertTrue(
                json_file.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                json_file_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_binary_data_outputpath(self):
        """
        When Item has binary data - like layer packages, ensure Item.download() downloads file
        into that path instead of returning None or binary stream.
        :return:
        """
        try:
            JSON_item = self.gis.content.search("set1_mmpk_usa", "Mobile Map Package")[
                0
            ]
            with tempfile.TemporaryDirectory() as temp_dir:
                json_file = JSON_item.download(save_path=temp_dir)
                json_file_size = os.stat(json_file).st_size

            self.assertIsInstance(
                json_file,
                str,
                "Calling download() on mmpk item does not return download str path",
            )
            self.assertTrue(
                json_file.startswith(str(temp_dir)),
                "Download file name does not match known input",
            )
            self.assertGreater(
                json_file_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_Image(self):
        """
        For Image item, item.get_data(False) should return string representation of the item.
        :return:
        """
        try:
            data_item = self.gis.content.search(
                "set1_shifting_opportunity.png", "Image"
            )[0]
            with tempfile.TemporaryDirectory() as temp_dir:
                item_data = data_item.download()
                data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling download() on Image item does not return download str path",
            )
            self.assertTrue(
                item_data.endswith(".png"),
                "Download file name does not match known input",
            )
            self.assertGreater(
                data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_download_method_zero_size_data(self):
        """
        When Item has no data or 0kb size - ensure Item.download() returns None
        :return:
        """
        try:
            JSON_item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            json_file = JSON_item.download()
            json_file_size = os.stat(json_file).st_size
            self.assertIsNotNone(
                json_file, "Calling download() on zero kb item returns None"
            )
            self.assertEqual(json_file_size, 0, "Downloaded file size is not 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_binary_data_tryjson_True(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path even if try_json is set to True
        :return:
        """
        try:
            item = self.gis.content.search("set1_lpk", "Layer Package")[0]
            item_data = item.get_data(try_json=True)
            item_data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on lpk item does not return download str path",
            )
            self.assertTrue(
                item_data.startswith(str(tempfile.gettempdir())),
                "Download file name does not match known input",
            )
            self.assertGreater(
                item_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_binary_data_tryjson_False(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path when try_json is set to False
        :return:
        """
        try:
            item = self.gis.content.search("set1_geometric", "Map Document")[0]
            item_data = item.get_data(try_json=False)
            item_data_size = os.stat(item_data).st_size

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on map doc item does not return download str path",
            )
            self.assertTrue(
                item_data.startswith(str(tempfile.gettempdir())),
                "Download file name does not match known input",
            )
            self.assertGreater(
                item_data_size, 0, "Downloaded file size is not greater than 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_JSON_data_tryjson_False(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json False,
        should return the data as str instead of dict
        :return:
        """
        try:
            item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            item_data = item.get_data(try_json=False)

            self.assertIsInstance(
                item_data,
                str,
                "Calling get_data() on web map item does not return data as str with try_json is false",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_JSON_data_tryjson_True(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json True,
        should return the data dict instead of str
        :return:
        """
        try:
            item = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
            item_data = item.get_data(try_json=True)

            self.assertIsInstance(
                item_data,
                dict,
                "Calling get_data() on web map item does not return data as dict with try_json is true",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_zero_size_data_tryjson_False(self):
        """
        When Item has no data, calling Item.get_data() with try_json False,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            item_data = item.get_data(try_json=False)

            self.assertIsNone(
                item_data,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_zero_size_data_tryjson_True(self):
        """
        When Item has no data, calling Item.get_data() with try_json True,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            item_data = item.get_data(try_json=True)

            self.assertEqual(
                len(item_data),
                0,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_get_data_method_empty_data_tryjson_True(self):
        """
        When Item has no data, but item.size > 0, calling Item.get_data() with try_json True,
        should return None.
        :return:
        """
        try:
            item = self.gis.content.get("6e39ae0904a8484786a0121a01fcedf1")
            self.assertGreater(
                item.size,
                0,
                "Invalid item for this testcase, its size is not greater than 0",
            )

            item_data = item.get_data(try_json=True)

            self.assertEqual(
                len(item_data),
                0,
                "Calling get_data() on empty item with tryjson False does not return None",
            )
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_overwrite_item(self):
        """
        Update a csv item with new csv file. Ensure the contents are updated and
        itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(self.gis, "set1_overwrite_old", "CSV")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
        # endregion

        try:
            # upload csv item
            csv_path = os.path.join(self.qalab_cls_path, "set1_overwrite_old.csv")
            csv_item = self.gis.content.add({}, data=csv_path)

            self.assertIsNotNone(csv_item, "Cannot add csv item")
            old_item_id = csv_item.id

            # update csv item
            new_csv_path = os.path.join(self.qalab_cls_path, "set1_overwrite_new.csv")
            item_update_result = csv_item.update({}, data=new_csv_path)
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )
            new_item_id = csv_item.id

            self.assertEqual(
                old_item_id, new_item_id, "Item ID is not same after overwriting"
            )

            # verify content is updated
            csv_download_path = csv_item.download()

            # read contents
            new_df = read_csv(new_csv_path)
            downloaded_file_df = read_csv(csv_download_path)
            self.assertEqual(
                new_df.shape,
                downloaded_file_df.shape,
                "The number of rows cols of csv item not same as updated csv file",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_register_application(self):
        """tests the registering of an Application item"""
        try:
            content = self.gis.content
            res = []
            for at in ["browser", "native", "server", "multiple"]:
                ip = {
                    "title": uuid.uuid4().hex,
                    "tags": "test1,test2,test3,test4",
                    "type": "Application",
                }
                item = content.add(item_properties=ip)
                reg = item.register(app_type=at)
                res.append(isinstance(reg, dict))
                item.delete()
            self.assertTrue(all(res))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_application_info(self):
        """tests the application information property is working"""
        try:
            content = self.gis.content
            res = []
            for at in ["multiple"]:
                ip = {
                    "title": uuid.uuid4().hex,
                    "tags": "test1,test2,test3,test4",
                    "type": "Application",
                }
                item = content.add(item_properties=ip)
                reg = item.register(app_type=at)
                appinfo = item.app_info
                res.append(isinstance(appinfo, dict) and len(appinfo) > 0)
                item.delete()
            self.assertTrue(all(res))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_unregister_application(self):
        """tests the unregistering of an Application item"""
        try:
            content = self.gis.content
            res = []
            for at in ["multiple"]:
                ip = {
                    "title": uuid.uuid4().hex,
                    "tags": "test1,test2,test3,test4",
                    "type": "Application",
                }
                item = content.add(item_properties=ip)
                reg = item.register(app_type=at)
                unreg = item.unregister()
                res.append(unreg)
                item.delete()
            self.assertTrue(all(res))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_overwrite_manyHFS_using_csv_errors(self):
        """
        Multiple feature layers are published using a csv. Trying to overwrite this should raise RunTime Error
        :return:
        """

        try:
            # update csv item
            new_csv_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_manyHFS_csv.csv"
            )
            item_update_result = self.one_to_many_csv_item[0].update(
                {}, data=new_csv_path
            )
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )
            print("CSV item updated")

            # overwrite the feature layer
            with self.assertRaises(RuntimeError):
                self.one_to_many_csv_item[0].publish(overwrite=True)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "")
    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(
            self.gis, "title:set1_overwrite_HFS_csv2.csv", "CSV"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest("Cannot delete old CSV output. Skipping test.")
            else:
                print("Deleted old csv output")

        old_wfl_sr = PortalUtils.search_portal_item(
            self.gis, "set1_overwrite_HFS_csv2", "Feature Service"
        )
        if old_wfl_sr is not None:
            delete_result2 = PortalUtils.delete_portal_item(self.gis, old_wfl_sr)
            if not delete_result2:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
            else:
                print("Deleted old Feature Service output")
        # endregion

        try:
            # upload fgdb item
            csv_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_csv2.csv")
            csv_item = self.gis.content.add({}, data=csv_path)
            self.assertIsNotNone(csv_item, "Cannot add csv item")

            # publish the fgdb item
            wfl_item = csv_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish csv into a feature service")
            old_wfl_item_id = wfl_item.id
            old_flayer = wfl_item.layers[0]
            old_fset = old_flayer.query()
            old_flayer_df = old_fset.sdf

            # update fdgb item
            new_csv_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_csv2.csv"
            )
            item_update_result = csv_item.update({}, data=new_csv_path)
            self.assertTrue(
                item_update_result, "Calling update on csv item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = csv_item.publish(overwrite=True)
            print(overwrite_result)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                old_wfl_item_id,
                new_wfl_item_id,
                "Item ID is not same after overwriting",
            )

            # verify content is updated
            flayer = overwrite_result.layers[0]
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            print("Old flayer shape: " + str(old_flayer_df.shape))
            print("flayer shape after overwrite: " + str(overwritten_flayer_df.shape))
            self.assertGreater(
                overwritten_flayer_df.shape[0],
                old_flayer_df.shape[0],
                "Number of rows did not increase after overwriting per expectation",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "")
    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(
            self.gis, "title:set1_Item_overwrite_HFS_fgdb.gdb", "File Geodatabase"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest("Cannot delete old fgdb output. Skipping test.")
            else:
                print("Deleted old fgdb output")

        old_wfl_sr = PortalUtils.search_portal_item(
            self.gis, "set1_Item_overwrite_HFS_fgdb", "Feature Service"
        )
        if old_wfl_sr is not None:
            delete_result2 = PortalUtils.delete_portal_item(self.gis, old_wfl_sr)
            if not delete_result2:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
            else:
                print("Deleted old Feature Service output")
        # endregion

        try:
            # upload fgdb item
            fgdb_path = os.path.join(
                self.qalab_cls_path, "set1_Item_overwrite_HFS_fgdb.gdb.zip"
            )
            fgdb_item = self.gis.content.add({}, data=fgdb_path)
            self.assertIsNotNone(fgdb_item, "Cannot add fgdb item")

            # publish the fgdb item
            wfl_item = fgdb_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish fgdb into a feature service")
            old_wfl_item_id = wfl_item.id
            old_flayer = wfl_item.layers[0]
            old_fset = old_flayer.query()
            old_flayer_df = old_fset.sdf

            # update fdgb item
            new_fgdb_path = os.path.join(
                self.qalab_cls_path,
                "overwrite_wfl",
                "set1_Item_overwrite_HFS_fgdb.gdb.zip",
            )
            item_update_result = fgdb_item.update({}, data=new_fgdb_path)
            self.assertTrue(
                item_update_result, "Calling update on fgdb item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = fgdb_item.publish(overwrite=True)
            print(overwrite_result)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                old_wfl_item_id,
                new_wfl_item_id,
                "Item ID is not same after overwriting",
            )

            # verify content is updated
            flayer = overwrite_result.layers[0]
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            print("Old flayer shape: " + str(old_flayer_df.shape))
            print("flayer shape after overwrite: " + str(overwritten_flayer_df.shape))
            self.assertGreater(
                overwritten_flayer_df.shape[0],
                old_flayer_df.shape[0],
                "Number of rows did not increase after overwriting per expectation",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(True, "Duplicate test, turn off for speed")
    def test_overwrite_HFS_using_shp(self):
        """
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(
            self.gis, "title:set1_overwrite_HFS_shp", "Shapefile"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest("Cannot delete old shp output. Skipping test.")
            else:
                print("Deleted old shp output")

        old_wfl_sr = PortalUtils.search_portal_item(
            self.gis, "set1_overwrite_HFS_shp", "Feature Service"
        )
        if old_wfl_sr is not None:
            delete_result2 = PortalUtils.delete_portal_item(self.gis, old_wfl_sr)
            if not delete_result2:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
            else:
                print("Deleted old Feature Service output")
        # endregion

        try:
            # upload shp item
            shp_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_shp.zip")
            shp_item = self.gis.content.add({}, data=shp_path)
            self.assertIsNotNone(shp_item, "Cannot add shp item")

            # publish the shp item
            wfl_item = shp_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish shp into a feature service")
            old_wfl_item_id = wfl_item.id
            old_flayer = wfl_item.layers[0]
            old_fset = old_flayer.query()
            old_flayer_df = old_fset.sdf

            # update shp item
            new_shp_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_shp.zip"
            )
            item_update_result = shp_item.update({}, data=new_shp_path)
            self.assertTrue(
                item_update_result, "Calling update on shp item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = shp_item.publish(overwrite=True)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                old_wfl_item_id,
                new_wfl_item_id,
                "Item ID is not same after overwriting",
            )

            # verify content is updated
            flayer = overwrite_result.layers[0]
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertGreater(
                overwritten_flayer_df.shape[0],
                old_flayer_df.shape[0],
                "Number of rows needs to be more after overwriting",
            )
            self.assertEqual(
                (old_flayer_df.shape[0] + 10, old_flayer_df.shape[1]),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Duplicate test, turn off for speed")
    def test_overwrite_HFS_using_sd(self):
        """
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region delete old service on portal
        old_sr = PortalUtils.search_portal_item(
            self.gis, "title:set1_overwrite_HFS_sd", "Service Definition"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                raise unittest.SkipTest("Cannot delete old sd output. Skipping test.")
            else:
                print("Deleted old sd output")

        old_wfl_sr = PortalUtils.search_portal_item(
            self.gis, "set1_overwrite_HFS_sd", "Feature Service"
        )
        if old_wfl_sr is not None:
            delete_result2 = PortalUtils.delete_portal_item(self.gis, old_wfl_sr)
            if not delete_result2:
                raise unittest.SkipTest(
                    "Cannot delete old service output. Skipping test."
                )
            else:
                print("Deleted old Feature Service output")
        # endregion

        try:
            # upload sd item
            sd_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_sd.sd")
            sd_item = self.gis.content.add({}, data=sd_path)
            self.assertIsNotNone(sd_item, "Cannot add sd item")

            # publish the sd item
            wfl_item = sd_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish sd into a feature service")
            old_wfl_item_id = wfl_item.id
            old_flayer = wfl_item.layers[0]
            old_fset = old_flayer.query()
            old_flayer_df = old_fset.sdf

            # update shp item
            new_sd_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_sd.sd"
            )
            item_update_result = sd_item.update({}, data=new_sd_path)
            self.assertTrue(
                item_update_result, "Calling update on sd item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = sd_item.publish(overwrite=True)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                old_wfl_item_id,
                new_wfl_item_id,
                "Item ID is not same after overwriting",
            )

            # verify content is updated
            flayer = overwrite_result.layers[0]
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertGreater(
                overwritten_flayer_df.shape[0],
                old_flayer_df.shape[0],
                "Number of rows needs to be more after overwriting",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_nonorg_public_Item_share_unshare_orggroup(self):
        """
        In AGOL, users can search for public items outside the org and share them to their group
        This is a popular way to accumulate content in their GIS.
        :return:
        """
        try:
            itemid = "8651e4d585654f6b955564efe44d04e5"
            data_item = self.gis.content.get(itemid)
            self.assertIsNotNone(
                data_item, "Cannot create an Item Obj using a non org public items id"
            )
            group3 = self.gis.groups.search("title:group3", max_groups=1)[0]

            # unshare form the group first
            unshare_result = data_item.unshare([group3])

            # get contents of group3 to verify it is unshared
            group3_content = group3.content()

            import time

            time.sleep(
                50
            )  # should find a way around waiting like this for cache is update

            interested_item = [i for i in group3_content if i.id == data_item.id]
            self.assertEqual(
                len(interested_item),
                0,
                "Shared item should not be found in group's contents",
            )

            # try sharing to the group in the org
            data_item.sharing.groups.add(group3)

            import time

            time.sleep(50)

            # get contents of group3 to verify
            group3_content = group3.content()

            time.sleep(50)

            interested_item = [i for i in group3_content if i.id == data_item.id]
            self.assertEqual(
                len(interested_item), 1, "Shared item not found in group's contents"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skip(
        "According to doc, dependent_upon() only works for Enterprise"
    )
    def test_dependent_upon_ownItems(self):
        """
        As an item owner, I should be able to get my Item's dependencies
        :return:
        """

        # get an item
        chicago_csv_item = self.gis.content.search("title:set1_Chicago", "CSV")[0]
        wm = self.gis.content.search("set1_cities_webmap", "Web Map")[0]
        print(wm)
        try:
            chicago_deps = chicago_csv_item.dependent_upon()
            wm_deps = wm.dependent_upon()

            # assert csv item dependency none
            self.assertIsNotNone(
                chicago_deps, "Unable to get dependencies for CSV item"
            )
            self.assertEqual(
                chicago_deps["total"],
                0,
                "A default CSV item should have 0 dependencies",
            )

            # assert webmap dependency
            self.assertIsNotNone(
                wm_deps, "Unable to get dependencies for a webmap item"
            )
            self.assertGreaterEqual(
                len(wm_deps["list"]),
                2,
                "at least 1 dependency should be found for cities webmap",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


@integration_test
class Test_Item_arcgis_kubernetes(unittest.TestCase):
    """
    Test to check if a Item object works with ArcGIS Online org
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal can be reached
        Get class test asset location
        :return:
        """
        cls.gis = GIS(profile="your_kubernetes_profile")
        if cls.gis is None:
            cls.class_skip = True

        # setup QALAB_ROOT_PATH
        if cls.gis is None:
            cls.class_skip = True
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_data_path = (
            cls.qalab_base_path + _conf_reader["test_data"]["qalab_dataprep"]
        )
        cls.qalab_cls_path = (
            cls.qalab_base_path + _conf_reader["test_data"]["qalab_Item_cls"]
        )

        # region publish necessary web layers
        cls.one_to_many_csv_item = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv", "CSV"
        )
        if not cls.one_to_many_csv_item:
            # upload csv item
            csv_path = os.path.join(
                cls.qalab_cls_path, "set1_overwrite_manyHFS_csv.csv"
            )
            cls.one_to_many_csv_item = cls.gis.content.add({}, data=csv_path)
            print("CSV item added")
            cls.assertIsNotNone(cls.one_to_many_csv_item, "Cannot add csv item")

        cls.one_to_many_wfl_item_1 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_1", "Feature Layer"
        )
        if not cls.one_to_many_wfl_item_1:
            # publish the csv item - 1
            cls.one_to_many_wfl_item_1 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_1"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_1, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_1")
            cls.one_to_many_wfl_item_1.update({"title": "set1_overwrite_manyHFS_csv_1"})

        cls.one_to_many_wfl_item_2 = PortalUtils.search_portal_item(
            cls.gis, "set1_overwrite_manyHFS_csv_2", "Feature Layer"
        )
        if not cls.one_to_many_wfl_item_2:
            # publish the csv item - 2
            cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_2"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_2, "Cannot publish CSV into a feature service"
            )
            print("Published " + "set1_overwrite_manyHFS_csv_2")
            cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})
        # endregion

        # region print banner
        print("==================================================================")
        print("Beginning tests in Test_Item_kubernetes_builtin class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_Item_"

        # region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(
            self.gis, self.test_case_name, None
        )

        if search_result is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, search_result)
            if not delete_result[0]:
                test_skip = True  # cannot run test case if old output is not deleted
                print("Failed to delete old test output: " + str(delete_result[1]))
            else:
                print("setUp : deleted old output. Proceeding to test case")
        else:
            print("setUp: not old outputs found. Proceeding to test case")
        # endregion

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    def test_publish_vtpk(self):
        vtpk_package_name = "set2_vtpk_worldgreen.vtpk"

        # region delete old service on portal
        service_title = os.path.splitext(vtpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Vector Tile Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for vtpk item
            sr = self.gis.content.search(
                vtpk_package_name, item_type="Vector Tile Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                vtpk_item = sr[0]
                print("Old VTPK item found and will be used")

            else:
                print("Old VTPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", vtpk_package_name
                )
                vtpk_item = self.gis.content.add(
                    {"type": "Vector Tile Package"}, file_path
                )

            # publish vtpk item
            publish_output = vtpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish VTPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Vector Tile Service",
                    "Publishing VPTK does not create an item "
                    "of type Vector Tile Service",
                )

                # validate service item has layers
                self.assertTrue(
                    len(publish_output.layers) > 0,
                    "No layers found in Vector Tile Service",
                )
                print("Passed: VTPK successfully published as VTS")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_publish_slpk(self):
        slpk_package_name = "set2_slpk_Vancouver.slpk"

        # region delete old service on portal
        service_title = os.path.splitext(slpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(
            self.gis, service_title, "Scene Service"
        )
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for slpk item
            sr = self.gis.content.search(
                slpk_package_name, item_type="Scene Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                slpk_item = sr[0]
                print("Old SLPK item found and will be used")

            else:
                print("Old SLPK not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", slpk_package_name
                )
                slpk_item = self.gis.content.add({"type": "Scene Package"}, file_path)

            # publish slpk item
            publish_output = slpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish SPK item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is scene service
                self.assertEqual(
                    publish_output.type,
                    "Scene Service",
                    "Publishing SLPK does not create an item " "of type Scene Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Scene Service")
                print("Passed: SLPK successfully published as Scene Layer")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_publish_tpkx(self):
        tpkx_package_name = "Riverside.tpkx"

        # region delete old service on portal
        service_title = os.path.splitext(tpkx_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, "Map Service")
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for tpkx item
            sr = self.gis.content.search(
                tpkx_package_name, item_type="Tile Package", max_items=1
            )
            if sr is not None and len(sr) > 0:
                tpkx_item = sr[0]
                print("Old TPKX item found and will be used")

            else:
                print("Old TPKX not found on portal. Adding new")
                file_path = os.path.join(
                    self.qalab_data_path, "packages", tpkx_package_name
                )
                tpkx_item = self.gis.content.add({"type": "Tile Package"}, file_path)

            # publish tpkx item
            publish_output = tpkx_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish TPKX item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Map Service",
                    "Publishing TPKX does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: TPKX successfully published as WTL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_publish_shp(self):
        zip_package_name = "set1_line.zip"

        # region delete old service on portal
        service_title = os.path.splitext(zip_package_name)[0]
        for service_type in ["Feature Service", "Map Service"]:
            old_sr = PortalUtils.search_portal_item(
                self.gis, service_title, service_type
            )
            if old_sr is not None:
                delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
                if not delete_result:
                    self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                zip_package_name, item_type="Shapefile", max_items=1
            )
            if sr is not None and len(sr) > 0:
                zip_item = sr[0]
                print("Old Zipped item found and will be used")

            else:
                print("Old zip not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "shp", zip_package_name)
                zip_item = self.gis.content.add({"type": "Shapefile"}, file_path)

            # publish tpk item
            publish_output = zip_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish ZIP item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Feature Service",
                    "Publishing SHP does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: Shapefile successfully published as HFL")

            tile_item = publish_output.create_tile_service(
                "Set1_Line_Shp", 1500000, 40000
            )
            print(tile_item)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_publish_fgdb(self):
        zip_package_name = "set2_USAcities.zip"

        # region delete old service on portal
        service_title = os.path.splitext(zip_package_name)[0]
        for service_type in ["Feature Service", "Map Service"]:
            old_sr = PortalUtils.search_portal_item(
                self.gis, service_title, service_type
            )
            if old_sr is not None:
                delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
                if not delete_result:
                    self.fail("Cannot delete old service output. Skipping test.")
        # endregion

        try:
            # search for spk item
            sr = self.gis.content.search(
                zip_package_name, item_type="File Geodatabase", max_items=1
            )
            if sr is not None and len(sr) > 0:
                zip_item = sr[0]
                print("Old Zipped item found and will be used")

            else:
                print("Old zip not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "fgdb", zip_package_name)
                zip_item = self.gis.content.add({"type": "File Geodatabase"}, file_path)

            # publish tpk item
            publish_output = zip_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish ZIP item")
            else:
                # validate return type
                self.assertIsInstance(
                    publish_output,
                    arcgis.gis.Item,
                    "item.publish does not return "
                    "an Item upon success. Instead it returns: "
                    + str(type(publish_output)),
                )

                # validate item's type is vector tile service
                self.assertEqual(
                    publish_output.type,
                    "Feature Service",
                    "Publishing SHP does not create an item " "of type Map Service",
                )

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: File Geodatabase successfully published as HFL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")


# TestModule
def tearDownModule():
    print("**End GIS module Tests**")


if __name__ == "__main__":
    unittest.main()
