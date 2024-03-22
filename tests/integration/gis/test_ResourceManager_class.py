# -------------------------------------------------------------------------------
# Name:        ResourceManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import os
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from integration.config import QALAB_ROOT_PATH
from configparser import ConfigParser
from pathlib import Path
import datetime
from utils.decorators import integration_test
import tempfile

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
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check

# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module ResourceManager class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


@integration_test
class Test_ResourceManager_portal(unittest.TestCase):
    """
    Test to check if a ResourceManager object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, "UTF-8")

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_data_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_dataprep"]
        )
        cls.qalab_cls_path = (
            cls.qalab_base_path
            + _conf_reader2["test_data"]["qalab_ResourceManager_cls"]
        )
        cls.qalab_output_root = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_output_root"]
        )
        cls.qalab_cls_name = _conf_reader2["test_data"]["qalab_ResourceManager_cls"]
        # endregion

        # region precondition checks and sign in
        cls.gis = GIS(profile="your_ent_admin_profile", verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_ResourceManager_portal class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_ResMgr_"

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
            "{0}_{1}_{2}_{3}_{4}_{5}",
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
    def test_add_resources_single_file_root(self):

        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])

        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            # add a json resource file
            file_to_add = os.path.join(self.qalab_cls_path, "root_resource_file.json")
            add_result = res_mgr.add(file_to_add)
            print(add_result)

            self.assertTrue(
                add_result["success"], "Failed to add resource file at root level"
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
    def test_add_resources_multi_files_folders(self):

        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding multiple resource files into folders",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])

        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            folder_to_add = os.path.join(self.qalab_cls_path, "set2_streets_night")

            # snake through and find all files in this dir
            full_file_list = [
                os.path.join(root, file)
                for root, dir, file_list in os.walk(folder_to_add)
                for file in file_list
            ]
            print(
                "Number of resources to be added in this test: "
                + str(len(full_file_list))
            )

            # loop through each file. Add containing folder hierarchy as prefixes
            for now_file in full_file_list:
                # string manipulation to find fold hierarchy
                now_file_path = Path(now_file)
                # prefixes start relative to folder containing these files
                leftStrippedPath = str(now_file_path.relative_to(folder_to_add))
                prefix, filename = leftStrippedPath.rsplit("\\", 1)
                prefix_safe = prefix.replace("\\", "/").replace(
                    " ", "_"
                )  # make URL safe

                # add the current resource
                print("Adding: " + prefix_safe + "/" + filename, end=" # ")
                add_result = res_mgr.add(now_file, folder_name=prefix_safe)
                print(add_result["success"])

                # validate then and there
                self.assertTrue(
                    add_result["success"], "Failed to add resource file: " + filename
                )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(True, "Test condition not met. Check if old outputs are present")
    def test_add_resources_archive(self):

        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])

        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            # add a json resource file
            file_to_add = os.path.join(
                self.qalab_cls_path, "set2_vtpk_style_canvasdark.zip"
            )
            add_result = res_mgr.add(file_to_add, archive=True)
            print(add_result)

            self.assertTrue(
                add_result["success"], "Failed to add resource file at root level"
            )

            # check the number of resources
            resource_list = res_mgr.list()
            print(
                "Number of resource files from archive upload: "
                + str(len(resource_list))
            )
            self.assertGreaterEqual(
                len(resource_list),
                1,
                "Number of resources did not increment for archive upload",
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
    def test_list_resources_small_anonymous_ago(self):

        # create anonymous connection to AGO
        _gis = GIS()

        # search for existing vector tile service item by Esri
        vtl_item = _gis.content.get(
            "86f556a2d1fd468181855a35e344567f"
        )  # World street map night

        if vtl_item is None:
            print(
                "Could not find Esri's vector tile service item: 92c551c9f07b4147846aae273e822714"
                + "Skipping test case."
            )
            raise unittest.SkipTest

        res_mgr = vtl_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            # get the list of resource files
            vtl_resources = res_mgr.list()
            self.assertIsNotNone(
                vtl_resources, "Got a none object when listing an item with resources"
            )
            print("Number of resource files: " + str(len(vtl_resources)))

            self.assertGreaterEqual(
                len(vtl_resources), 2, "Number of resource files less than usual"
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
    def test_list_resources_huge_anonymous_ago(self):

        # create anonymous connection to AGO
        _gis = GIS()

        # search for existing vector tile service item by Esri
        # World Street Map (with Relief) (Mature Support)
        vtl_item = _gis.content.get("fdf540eef40344b79ead3c0c49be76a9")

        if vtl_item is None:
            print(
                "Could not find Esri's vector tile service item: fdf540eef40344b79ead3c0c49be76a9"
                + "Skipping test case."
            )
            raise unittest.SkipTest

        res_mgr = vtl_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            # get the list of resource files
            vtl_resources = res_mgr.list()
            self.assertIsNotNone(
                vtl_resources, "Got a none object when listing an item with resources"
            )
            print("Number of resource files: " + str(len(vtl_resources)))

            self.assertGreaterEqual(
                len(vtl_resources), 700, "Number of resource files less than usual"
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
    def test_get_resource_json_file_public_item(self):

        # create anonymous connection to AGO
        _gis = GIS()

        # search for existing vector tile service item by Esri
        # Existing vector tile service from Esri
        vtl_item = _gis.content.get("86f556a2d1fd468181855a35e344567f")

        if vtl_item is None:
            print(
                "Could not find Esri's vector tile service item: 92c551c9f07b4147846aae273e822714"
                + "Skipping test case."
            )
            raise unittest.SkipTest

        res_mgr = vtl_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            # get the info/root.json file
            root_json = res_mgr.get("info/root.json")
            self.assertIsNotNone(root_json, "Got none when getting resource file")
            self.assertIsInstance(
                root_json, dict, "Got a non dict object for JSON resource file"
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
    def test_get_resource_bin_file_private_item_defaults(self):

        # create a new item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])
        else:
            raise unittest.SkipTest

        # get the resource manager
        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        # add an image file
        file_to_add = os.path.join(self.qalab_cls_path, "set2_fld_bin_res_file.png")
        add_result = res_mgr.add(file_to_add, folder_name="fld")
        print(add_result)
        self.assertTrue(
            add_result["success"], "Failed to add resource file at root level"
        )

        # get the info/root.json file
        try:
            fld_png = res_mgr.get("fld/set2_fld_bin_res_file.png")
            self.assertIsNotNone(fld_png, "Got none when getting resource file")
            self.assertTrue("Temp" in fld_png, "file does not download to temp dir")

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
    def test_get_resource_bin_file_custom_download(self):

        # create a new item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])
        else:
            raise unittest.SkipTest

        # get the resource manager
        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        # add an image file
        file_to_add = os.path.join(self.qalab_cls_path, "set2_fld_bin_res_file.png")
        add_result = res_mgr.add(file_to_add, folder_name="fld")

        # add json file
        file_to_add2 = os.path.join(self.qalab_cls_path, "root_resource_file.json")
        add_result2 = res_mgr.add(file_to_add2, folder_name="fld")

        self.assertTrue(
            add_result2["success"] and add_result["success"],
            "Failed to add resource files",
        )

        # Download both json and png files to disk overriding defaults
        try:
            with tempfile.TemporaryDirectory() as output_folder:
                fld_png = res_mgr.get(
                    "fld/set2_fld_bin_res_file.png",
                    out_folder=output_folder,
                    out_file_name="a_sequoias_seed_is_tiny.png",
                )
                fld_json = res_mgr.get(
                    "fld/root_resource_file.json",
                    try_json=False,
                    out_folder=output_folder,
                    out_file_name="as_its_a_type_of_pine.json",
                )
                self.assertIsNotNone(fld_png, "Got none when getting png resource file")
                self.assertIsNotNone(fld_json, "Got none when getting json resource file")
                self.assertTrue(
                    "a_sequoias_seed_is_tiny.png" in fld_png,
                    "png file does not download with custom name",
                )
                self.assertTrue(
                    output_folder in fld_png, "png file does not download to custom dir"
                )

                self.assertTrue(
                    "as_its_a_type_of_pine.json" in fld_json,
                    "json file does not download with custom name",
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
    def test_update_resource_json_file(self):

        # create a new item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])
        else:
            raise unittest.SkipTest

        # get the resource manager
        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        # add an image file
        file_to_add = os.path.join(self.qalab_cls_path, "set2_fld_bin_res_file.png")
        add_result = res_mgr.add(file_to_add, folder_name="fld")

        # add json file
        file_to_add2 = os.path.join(self.qalab_cls_path, "root_resource_file.json")
        file_to_update = os.path.join(
            self.qalab_cls_path, "overwrite", "root_resource_file.json"
        )
        add_result2 = res_mgr.add(file_to_add2, folder_name="fld")

        self.assertTrue(
            add_result2["success"] and add_result["success"],
            "Failed to add resource files",
        )

        # Read the JSON file, update then read the update to ensure its changed
        try:
            original_json = res_mgr.get("fld/root_resource_file.json", try_json=True)
            self.assertIsInstance(
                original_json, dict, "Did not get dict when getting json resource file"
            )
            self.assertTrue(
                original_json["text"] == "hello arcgis",
                "content of original JSON file is wrong",
            )

            # update
            update_result = res_mgr.update(file_to_update, folder_name="fld")
            updated_json = res_mgr.get("fld/root_resource_file.json", try_json=True)
            self.assertIsInstance(
                updated_json, dict, "Did not get dict when getting json resource file"
            )
            self.assertTrue(
                updated_json["text"] == "hello Python folks",
                "contents of updated JSON file is wrong",
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
    def test_remove_resource_one_file(self):

        # create a new item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding resource files",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])
        else:
            raise unittest.SkipTest

        # get the resource manager
        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        # add an image file
        file_to_add = os.path.join(self.qalab_cls_path, "set2_fld_bin_res_file.png")
        add_result = res_mgr.add(file_to_add, folder_name="fld")

        # add json file
        file_to_add2 = os.path.join(self.qalab_cls_path, "root_resource_file.json")
        add_result2 = res_mgr.add(file_to_add2, folder_name="fld")

        self.assertTrue(
            add_result2["success"] and add_result["success"],
            "Failed to add resource files",
        )

        # Get list of resources, then remove the image file and check the list of resource files
        try:
            original_list = res_mgr.list()
            self.assertEqual(
                len(original_list), 2, "Number of original resources is not 2"
            )

            # remove json file in folder
            remove_result = res_mgr.remove("fld/root_resource_file.json")
            if not remove_result:
                print(remove_result)
            self.assertIsInstance(
                remove_result, bool, "Did not get bool when removing json resource file"
            )
            self.assertTrue(remove_result, "Failed to remove JSON file")

            res_list_after_removal = res_mgr.list()
            self.assertEqual(
                len(res_list_after_removal),
                1,
                "Number of resources after removal is not 1",
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
    def test_remove_resources_all_files(self):

        # create a vector tile service item
        item_properties_dict = {
            "title": self.namePrefix + self._testMethodName,
            "type": "Vector Tile Service",
            "snippet": "For unit test to check adding multiple resource files into folders",
            "tags": "unittest",
            "url": r"https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer",
        }

        added_item = self.gis.content.add(item_properties_dict)
        if added_item is not None:
            print("Created Vector tile service item: " + item_properties_dict["title"])

        res_mgr = added_item.resources
        self.assertIsInstance(
            res_mgr,
            arcgis.gis.ResourceManager,
            "item.resources does not return"
            "an object of type arcgis.gis.ResourceManager. "
            "Instead returns " + str(type(res_mgr)),
        )
        try:
            folder_to_add = os.path.join(self.qalab_cls_path, "set2_streets_night")

            # snake through and find all files in this dir
            full_file_list = [
                os.path.join(root, file)
                for root, dir, file_list in os.walk(folder_to_add)
                for file in file_list
            ]
            print(
                "Number of resources to be added in this test: "
                + str(len(full_file_list))
            )

            # loop through each file. Add containing folder hierarchy as prefixes
            for now_file in full_file_list:
                # string manipulation to find fold hierarchy
                now_file_path = Path(now_file)
                # prefixes start relative to folder containing these files
                leftStrippedPath = str(now_file_path.relative_to(folder_to_add))
                prefix, filename = leftStrippedPath.rsplit("\\", 1)
                prefix_safe = prefix.replace("\\", "/").replace(
                    " ", "_"
                )  # make URL safe

                # add the current resource
                print("Adding: " + prefix_safe + "/" + filename, end=" # ")
                add_result = res_mgr.add(now_file, folder_name=prefix_safe)
                print(add_result["success"])

                # validate then and there
                self.assertTrue(
                    add_result["success"], "Failed to add resource file: " + filename
                )

            # assert number of resources
            original_list = res_mgr.list()
            self.assertGreaterEqual(
                len(original_list), 5, "Number of original resources is not at least 5"
            )

            # remove all resources
            remove_result = (
                res_mgr.remove()
            )  # checking if not specifying anything deletes all files.
            if not remove_result:
                print(remove_result)
            self.assertIsInstance(
                remove_result, bool, "Did not get bool when removing all resource files"
            )
            self.assertTrue(remove_result, "Failed to remove all files")

            res_list_after_removal = res_mgr.list()
            self.assertEqual(
                len(res_list_after_removal),
                0,
                "Number of resources after removing all is not 0",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


# TestModule
def tearDownModule():
    print("**End GIS module Tests**")
