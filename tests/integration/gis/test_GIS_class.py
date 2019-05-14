#-------------------------------------------------------------------------------
# Name:        GIS class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime

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
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module GIS class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_GIS_ago(unittest.TestCase):
    """
    Test to check if a GIS object can be created with AGO
    """
    # portal_url = ""
    # portal_username = ""
    # portal_password = ""

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['arcgiscom']['url']
        cls.portal_username = _conf_reader['arcgiscom']['admin_user']
        cls.portal_password = _conf_reader['arcgiscom']['admin_password']

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_GIS_ago class")

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

    def test_sign_in(self):
        try:
            gis = GIS(self.portal_url, self.portal_username, self.portal_password)
            self.assertIsNotNone(gis, "Cannot sign into portal")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Sign in failed. Skipping test case")
    def test_properties(self):
        gis = GIS(self.portal_url, self.portal_username, self.portal_password)
        try:
            gis_properties = gis.properties
            self.assertIsNotNone(gis_properties, "gis.properties returns None")
            # weak assertion
            self.assertGreaterEqual(len(gis_properties), 20, "gis.properties may not be fully hydrated")

        except KeyError as ke:
            self.fail("Accessing gis.properties raises exception: " + str(ke))

        except unittest.SkipTest as skipException:
            raise skipException
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

class Test_GIS_portal(unittest.TestCase):
    """
    Test to check if a GIS object can be created with Portal
    """

    # portal_url = ""
    # portal_username = ""
    # portal_password = ""

    @classmethod
    def setUpClass(cls):
        """
        Check if portal can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['publisher1']
        cls.portal_password = _conf_reader['teamportal']['publisher1_password']

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_GIS_portal class")

    def setUp(self):
        print("Test: " + self._testMethodName)
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

    def test_sign_in(self):
        try:
            gis = GIS(self.portal_url, self.portal_username, self.portal_password)
            self.assertIsNotNone(gis, "Cannot sign into portal")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Sign in failed. Skipping test case")
    def test_properties(self):
        gis = GIS(self.portal_url, self.portal_username, self.portal_password)
        try:
            gis_properties = gis.properties
            self.assertIsNotNone(gis_properties, "gis.properties returns None")
            # weak assertion
            self.assertGreaterEqual(len(gis_properties), 20, "gis.properties may not be fully hydrated")

        except KeyError as ke:
            self.fail("Accessing gis.properties raises exception: " + str(ke))

        except unittest.SkipTest as skipException:
            raise skipException
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


#TestModule
def tearDownModule():
    print("**End GIS module Tests**")