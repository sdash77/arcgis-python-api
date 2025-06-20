# -------------------------------------------------------------------------------
# Name:        ImageryLayer class tests
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
    Set up code for full arcgis.raster module ImageryLayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


@integration_test
class Test_ImageryLayer_portal(unittest.TestCase):
    """
    Test to check if a ImageryLayer object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # region Read config data
        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_data_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_dataprep"]
        )
        cls.qalab_cls_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_ImageryLayer_cls"]
        )
        cls.qalab_output_root = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_output_root"]
        )
        cls.qalab_cls_name = _conf_reader2["test_data"]["qalab_ImageryLayer_cls"]
        # endregion

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(GIS(profile="your_enterprise_profile").url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(
            profile="your_enterprise_profile", verify_cert=False
        )
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_ImageryLayer_portal class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_ImgLyr_"

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
    def test_raster_mod_classes(self):
        try:
            # search for imagery layer and see if it can be accessed as a ImageryLayer class
            search_result = PortalUtils.search_portal_item(
                self.gis, "ImgSrv_Landast_Montana2014", "Image Service"
            )

            montana_img_lyr = search_result.layers[0]

            # assert
            self.assertIsInstance(
                montana_img_lyr,
                arcgis.raster.ImageryLayer,
                "Layers property of Img Service item does not return ImageryLayer obj",
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
    def test_has_histograms(self):
        try:
            # search for imagery layer and see if it can be accessed as a ImageryLayer class
            search_result = PortalUtils.search_portal_item(
                self.gis, "ImgSrv_Landast_Montana2014", "Image Service"
            )

            montana_img_lyr = search_result.layers[0]

            # assert
            has_hist = montana_img_lyr.properties.hasHistograms

            self.assertIsInstance(has_hist, bool, "Cannot access hasHistograms")

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
    def test_histograms(self):
        try:
            # search for imagery layer and see if it can be accessed as a ImageryLayer class
            search_result = PortalUtils.search_portal_item(
                self.gis, "Montana_Burn_scars14854", "Image Service"
            )

            montana_img_lyr = search_result.layers[0]

            # get histograms
            hist_all_bands = montana_img_lyr.histograms
            hist_b1 = hist_all_bands[0]
            counts_b1 = hist_b1["counts"]

            self.assertIsInstance(hist_all_bands, list, "Cannot access hasHistograms")
            self.assertEqual(len(hist_all_bands), 3, "cannot get 3 hist for 8 bands")

            self.assertIsInstance(hist_b1, dict, "histogram of a band is not a dict")
            self.assertEqual(
                len(counts_b1),
                hist_b1["size"],
                "length of counts list should be equal to size kvp",
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
