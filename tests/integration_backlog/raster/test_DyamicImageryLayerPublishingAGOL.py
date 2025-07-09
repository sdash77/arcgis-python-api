# -------------------------------------------------------------------------------
# Name:        Dynamic Imagery Layer publishing (AGOL) tests
# Purpose:     smoke tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
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
    from arcgis.raster.analytics import create_image_collection
    from arcgis.raster import RasterCollection
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
class Test_DynamicImageryPublishing(unittest.TestCase):
    """
    Publish Dynamic Imagery Layer (image collection) from local files
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

        cls.portal_url = _conf_reader["rasterqa_ago"]["url"]
        cls.portal_username = _conf_reader["rasterqa_ago"]["qa_user"]
        cls.portal_password = _conf_reader["rasterqa_ago"]["qa_password"]

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = _conf_reader2["test_data"]["qalab_base_path"]
        cls.qalab_data_path = (
            cls.qalab_base_path
            + _conf_reader2["test_data"]["qalab_ImageryLayerPublishingAGOL_data"]
        )

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(
            cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False
        )
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_DynamicImageryPublishing class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "Dynamic_ImgCol"

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
        self.test_case_name = (
            self.namePrefix + self._testMethodName + "_" + self.time_stamp
        )

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_image_collection_publishing(self):
        try:

            print(arcgis.__file__)

            img_col_item = create_image_collection(
                image_collection=self.test_case_name,
                input_rasters=self.qalab_data_path,
                raster_type_name="Raster Dataset",
                gis=self.gis,
            )

            print("Create Image Collection job completed")

            self.assertIsInstance(img_col_item, arcgis.gis.Item)

            img_lyr = img_col_item.layers[0]

            self.assertIsInstance(
                img_lyr,
                arcgis.raster.ImageryLayer,
                "Layers property of Img Service item does not return ImageryLayer object",
            )

            rc = RasterCollection(img_lyr.url, gis=self.gis)

            self.assertEqual(
                rc.count, 3, "Image collection doesn't contain all the items"
            )

            amberg_1_id = rc.get_field_values("Name").index("090160")
            ras = rc[amberg_1_id]["Raster"]

            # Tests for pixel data
            nd_array = ras.export_image(f="numpy_array")

            self.assertEqual(
                nd_array.shape, (450, 1200, 3), "Pixel data shape mismatch"
            )
            self.assertEqual(
                nd_array.mean(), 49.20380432098766, "Pixel data mean mismatch"
            )

            # delete the item
            self.assertTrue(img_col_item.delete())

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


def tearDownModule():
    print("**End GIS module Tests**")
