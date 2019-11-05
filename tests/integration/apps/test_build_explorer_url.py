#-------------------------------------------------------------------------------
# Name:        Explorer Integration Tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import collections

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    from arcgis.apps import build_explorer_url
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Tracks")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Explorer_Integrations(unittest.TestCase):
    """
    Test the creation of app url schemes
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        print("==================================================================")
        print("Beginning tests in Test_Explorer_Integrations class")

    def setUp(self):
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        self.item_id = "7584d0ac469748339004a01c80b55fc1"
        self.search = "Portland ME"
        self.bookmark = "Greater Portland, ME"
        self.center = "-123.456,56.987"
        self.scale = 500
        self.wkid = "4326"
        self.rotation = 180
        self.markup = True

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")


    def test_explorer_no_params(self):
        try:
            url = build_explorer_url()
            self.assertEqual(url, "https://explorer.arcgis.app")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_no_params_as_weblink(self):
        try:
            self.assertEqual(build_explorer_url(url_type="Web"), "https://explorer.arcgis.app")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_no_params_as_applink(self):
        try:
            url = build_explorer_url(url_type="App")
            self.assertEqual(url, "arcgis-explorer://")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_as_applink(self):
        try:
            url = build_explorer_url(webmap=self.item_id, url_type="App")
            self.assertEqual(url, "arcgis-explorer://?itemID={}".format(
                self.item_id
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_search_as_applink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     search=self.search,
                                     url_type="App")
            self.assertEqual(url, "arcgis-explorer://?itemID={}&search={}".format(
                self.item_id,
                "Portland%20ME"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_bookmark_as_applink(self):
        url = build_explorer_url(webmap=self.item_id,
                                 bookmark=self.bookmark,
                                 url_type="App")
        self.assertEqual(url, "arcgis-explorer://?itemID={}&bookmark={}".format(
            self.item_id,
            "Greater%20Portland,%20ME"
        ))

    def test_explorer_item_id_center_scale_as_applink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     url_type="App")
            self.assertEqual(url, "arcgis-explorer://?itemID={}&center={}&scale={}".format(
                self.item_id,
                self.center,
                self.scale
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_wkid_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     wkid=self.wkid)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_rotation_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     rotation=self.rotation)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&rotation={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.rotation
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_markup_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     markup=self.markup)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                str(self.markup).lower()
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_wkid_rotation_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     wkid=self.wkid,
                                     rotation=self.rotation)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&rotation={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid,
                self.rotation
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_wkid_markup_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     wkid=self.wkid,
                                     markup=self.markup)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid,
                str(self.markup).lower()
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_wkid_rotation_markup_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     wkid=self.wkid,
                                     rotation=self.rotation,
                                     markup=self.markup)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&rotation={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid,
                self.rotation,
                str(self.markup).lower()
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_item_id_center_scale_rotation_markup_as_weblink(self):
        try:
            url = build_explorer_url(webmap=self.item_id,
                                     center=self.center,
                                     scale=self.scale,
                                     rotation=self.rotation,
                                     markup=self.markup)
            self.assertEqual(url, "https://explorer.arcgis.app?itemID={}&center={}&scale={}&rotation={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.rotation,
                str(self.markup).lower()
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_incorrect_url_type(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(url_type="Fake")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_scale(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(webmap=self.item_id,
                                   center=self.center)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_search(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(search=self.search)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_bookmark(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(bookmark=self.bookmark)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_center(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(center=self.center)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_wkid(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(wkid=self.wkid)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_rotation(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(rotation=self.rotation)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_item_id_markup(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(markup=self.markup)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_center_wkid(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(wkid=self.wkid,
                                   webmap=self.item_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_center_rotation(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(rotation=self.rotation,
                                   webmap=self.item_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_no_center_markup(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(markup=self.markup,
                                   webmap=self.item_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_conflicting_params(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(search=self.search,
                                   bookmark=self.bookmark,
                                   webmap=self.item_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_explorer_exception_conflicting_params2(self):
        try:
            with self.assertRaises(ValueError):
                build_explorer_url(search=self.search,
                                   center=self.center,
                                   scale=self.scale,
                                   webmap=self.item_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End Explorer Integration Tests**")