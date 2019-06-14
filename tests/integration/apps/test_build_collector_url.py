#-------------------------------------------------------------------------------
# Name:        Collector Integration Tests
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
    from arcgis.apps import build_collector_url
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Collector Integration")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Collector_Integrations(unittest.TestCase):
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
        print("Beginning tests in Test_Collector_Integrations class")

    def setUp(self):
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        self.webmap = "7584d0ac469748339004a01c80b55fc1"
        self.center = "-123.456,45.6789"
        self.feature_layer = "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")


    def test_collector_feature_source_url(self):
        try:
            url = build_collector_url(webmap=self.webmap,
                                      center=self.center,
                                      feature_layer=self.feature_layer)
            self.assertEqual(url, "arcgis-collector://?itemID={}&center={}&featureSourceURL={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_center(self):
        try:
            url = build_collector_url(webmap=self.webmap,
                                      center=self.center)
            self.assertEqual(url, "arcgis-collector://?itemID={}&center={}".format(
                self.webmap,
                self.center
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_item_id(self):
        try:
            url = build_collector_url(webmap=self.webmap)
            self.assertEqual(url, "arcgis-collector://?itemID={}".format(
                self.webmap
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_no_params(self):
        try:
            url = build_collector_url()
            self.assertEqual(url, "arcgis-collector://")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_fields(self):
        try:
            url = build_collector_url(webmap=self.webmap,
                                      center=self.center,
                                      feature_layer=self.feature_layer,
                                      fields= {
                                       "name": "test name"
                                   })
            self.assertEqual(url, "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22name%22:%22test%20name%22%7D"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_multiple_fields(self):
        try:
            url = build_collector_url(webmap=self.webmap,
                                      center=self.center,
                                      feature_layer=self.feature_layer,
                                      fields=collections.OrderedDict([
                                       ("name", "test name"),
                                       ("name2", "test name2")
                                   ]))
            self.assertEqual(url, "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22name%22:%22test%20name%22,%22name2%22:%22test%20name2%22%7D"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_workforce(self):
        try:
            url = build_collector_url(webmap=self.webmap,
                                      center="${assignment.latitude},${assignment.longitude}",
                                      feature_layer=self.feature_layer,
                                      fields={
                                       "address": "${assignment.location}"
                                   })
            self.assertEqual(url, "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                "${assignment.latitude},${assignment.longitude}",
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22address%22:%22${assignment.location}%22%7D"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_exception_no_item_id_center(self):
        try:
            with self.assertRaises(ValueError):
                build_collector_url(center=self.center)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_exception_no_item_id_feature_source_url(self):
        try:
            with self.assertRaises(ValueError):
                build_collector_url(feature_layer=self.feature_layer)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_exception_no_item_id_fields(self):
        try:
            with self.assertRaises(ValueError):
                build_collector_url(fields={"name": "test"})
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_exception_no_item_id(self):
        try:
            with self.assertRaises(ValueError):
                build_collector_url(center=self.center,
                                 fields={"name": "test"})
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_collector_exception_no_feature_source_url(self):
        try:
            with self.assertRaises(ValueError):
                build_collector_url(webmap=self.webmap,
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
    print("**End Collector Integration Tests Tests**")