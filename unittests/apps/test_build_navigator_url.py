#-------------------------------------------------------------------------------
# Name:        Navigator Integration Tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from dino_utils.dino_precondition_checks import PreconditionChecks
from dino_utils.dino_configs import DinoConfigs
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
    from arcgis.apps import build_navigator_url
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Navigator Integrations")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Navigator_Integrations(unittest.TestCase):
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
        print("Beginning tests in Test_Navigator_Integrations class")

    def setUp(self):
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_navigator_no_params(self):
        try:
            self.assertEqual(build_navigator_url(), "arcgis-navigator://")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_one_stop_with_non_name(self):
        try:
            stop = ("-123.456,67.87",)
            url = build_navigator_url(stops=[stop])
            self.assertEqual(url, "arcgis-navigator://?stop={}".format(
                "-123.456,67.87"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_one_stop_with_name(self):
        try:
            stop = ("-123.456,67.87", "esri")
            url = build_navigator_url(stops=[stop])
            self.assertEqual(url, "arcgis-navigator://?stop={}&stopname={}".format(
                "-123.456,67.87",
                stop[1]
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_with_names(self):
        try:
            stops = [("-123.456,67.87", "esri office"), ("-123.654,34.45", "portland maine")]
            url = build_navigator_url(stops=stops)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stopname={}&stop={}&stopname={}".format(
                "-123.456,67.87",
                "esri%20office",
                "-123.654,34.45",
                "portland%20maine"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_one_name(self):
        try:
            stops = [("-123.456,67.87", "esri"), ("-123.654,34.45",)]
            with self.assertRaises(ValueError):
                build_navigator_url(stops=stops)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_no_names(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_optimize(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, optimize=True)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&optimize={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "true"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_navigate(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, navigate=True)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&navigate={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "true"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_navigate_optimize(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, navigate=True, optimize=True)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&optimize={}&navigate={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "true",
                "true"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_callback(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, callback="arcgis-collector://", callback_prompt="Collector for ArcGIS")
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&callback={}&callbackprompt={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "arcgis-collector://",
                "Collector%20for%20ArcGIS"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_callback_no_prompt(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, callback="arcgis-collector://")
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&callback={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "arcgis-collector://"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_travel_mode(self):
        try:
            stops = [("-123.456,67.87",), ("-123.654,34.45",)]
            url = build_navigator_url(stops=stops, travel_mode="Driving Time")
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&travelmode={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "Driving%20Time"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_two_stops_custom_travel_mode(self):
        try:
            stops = ["-123.456,67.87", "-123.654,34.45"]
            url = build_navigator_url(stops=stops, travel_mode="Custom Driving Time")
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}&travelmode={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "Custom%20Driving%20Time"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_stop_with_no_name(self):
        try:
            stops = ["-123.456,67.87", "-123.654,34.45"]
            url = build_navigator_url(stops=stops)
            self.assertEqual(url, "arcgis-navigator://?stop={}&stop={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_navigate_no_stops(self):
        try:
            with self.assertRaises(ValueError):
                build_navigator_url(navigate=True)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_optimize_no_stops(self):
        try:
            with self.assertRaises(ValueError):
                build_navigator_url(optimize=True)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_travel_mode_no_stops(self):
        try:
            with self.assertRaises(ValueError):
                build_navigator_url(travel_mode="Driving Time")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_navigator_callback_no_stops(self):
        try:
            with self.assertRaises(ValueError):
                build_navigator_url(callback="arcgis-collector://")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End Navigator Integration Tests**")