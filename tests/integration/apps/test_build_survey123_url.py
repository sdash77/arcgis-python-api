#-------------------------------------------------------------------------------
# Name:        Survey123 Integration Tests
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
    from arcgis.apps import build_survey123_url
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Survey123 Integrations")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Survey123_Integrations(unittest.TestCase):
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
        print("Beginning tests in Test_Survey123_Integrations class")

    def setUp(self):
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        self.item_id = "7584d0ac469748339004a01c80b55fc1"
        self.center = "-123.456,45.6789"
        self.fields = {"name": "value"}

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")


    def test_survey123_center(self):
        try:
            url = build_survey123_url(survey=self.item_id,
                                      center=self.center)
            self.assertEqual(url, "arcgis-survey123://?itemID={}&center={}".format(
                self.item_id,
                self.center
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_item_id(self):
        try:
            url = build_survey123_url(survey=self.item_id)
            self.assertEqual(url, "arcgis-survey123://?itemID={}".format(
                self.item_id
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_no_params(self):
        try:
            url = build_survey123_url()
            self.assertEqual(url, "arcgis-survey123://")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_field(self):
        try:
            url = build_survey123_url(survey=self.item_id,
                                      center=self.center,
                                      fields=self.fields)
            self.assertEqual(url, "arcgis-survey123://?itemID={}&center={}&field:{}={}".format(
                self.item_id,
                self.center,
                "name",
                "value"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_fields(self):
        try:
            url = build_survey123_url(survey=self.item_id,
                                      center=self.center,
                                      fields=collections.OrderedDict([
                                       ("name", "value"),
                                       ("description", "text")
                                   ]))
            self.assertEqual(url, "arcgis-survey123://?itemID={}&center={}&field:{}={}&field:{}={}".format(
                self.item_id,
                self.center,
                "name",
                "value",
                "description",
                "text"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_workforce(self):
        try:
            url = build_survey123_url(survey=self.item_id,
                                      center="${assignment.latitude},${assignment.longitude}",
                                      fields={"name": "${assignment.description}"})
            self.assertEqual(url, "arcgis-survey123://?itemID={}&center={}&field:{}".format(
                self.item_id,
                "${assignment.latitude},${assignment.longitude}",
                "name=${assignment.description}"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_all(self):
        try:
            url = build_survey123_url(survey="36ff9e8c13e042a58cfce4ad87f55d19",
                                      center="37.8199,-122.4783",
                                      fields={
                                       "surname": "Klauser Test"
                                   })
            self.assertEqual(url, "arcgis-survey123://?itemID=36ff9e8c13e042a58cfce4ad87f55d19&center=37.8199,-122.4783&field:surname=Klauser%20Test")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_exception_no_item_id_center(self):
        try:
            with self.assertRaises(ValueError):
                build_survey123_url(center=self.center)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_exception_no_item_id_fields(self):
        try:
            with self.assertRaises(ValueError):
                build_survey123_url(fields={"name": "test"})
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_survey123_exception_no_item_id(self):
        try:
            with self.assertRaises(ValueError):
                build_survey123_url(center=self.center,
                                 fields={"name": "test"})
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End Survey123 Integration Tests**")