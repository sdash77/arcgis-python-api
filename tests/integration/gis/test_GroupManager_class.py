#-------------------------------------------------------------------------------
# Name:        ContentManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
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
    import arcgis
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

class Test_GroupManager_portal_builtin(unittest.TestCase):
    """
    Test to check if a GroupManager object works with builtin portal
    """
    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        #region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['admin_user']
        cls.portal_password = _conf_reader['teamportal']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_GroupManager_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_GroupManager_portal_builtin class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_GroupManager_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_search_groups_150_default(self):
        """
        Number of groups exceeds the amount returned in a single call. Paging gets implemented. This test checks if
        GroupManager class works under paging using default parameters.
        :return:
        """
        try:
            group_search_result = self.gis.groups.search(query = "")

            print("Number of groups returned in search: " + str(len(group_search_result)))

            self.assertGreaterEqual(len(group_search_result),150, "Search did not return all groups when used with default parameters")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_search_groups_150_owner(self):
        """
        Number of groups exceeds the amount returned in a single call. Paging gets implemented. This test checks if
        GroupManager class works under paging when using a query that returns greater than 100 results
        :return:
        """
        try:
            group_search_result = self.gis.groups.search(query="owner: " + self.portal_username)

            print("Number of groups returned in search: " + str(len(group_search_result)))

            self.assertGreaterEqual(len(group_search_result), 150,
                                    "Search did not return > 150 groups when used with query parameters")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_search_groups_150_le100(self):
        """
        Number of groups exceeds the amount returned in a single call. Paging gets implemented. This test checks if
        GroupManager class works under paging when using a query that returns less than 100 results
        :return:
        """
        try:
            group_search_result = self.gis.groups.search(query="title: group_150_2*")
            # Should return all groups that end with 2x such as group_150_2, group_150_2(0,1,2 .. 9)
            # resulting in a total of 11

            print("Number of groups returned in search: " + str(len(group_search_result)))

            self.assertLessEqual(len(group_search_result), 100,
                                    "Search did not return <=100 when used with query parameters")
            self.assertEqual(len(group_search_result), 11, "Group search did not return exactly 11 groups")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_search_groups_150_max50(self):
        """
        Number of groups exceeds the amount returned in a single call. Paging gets implemented. This test checks if
        GroupManager class works under paging when max results is reduced to 50 from a default 2000
        :return:
        """
        try:
            group_search_result = self.gis.groups.search(query="owner: " + self.portal_username, max_groups = 50)

            print("Number of groups returned in search: " + str(len(group_search_result)))

            self.assertLessEqual(len(group_search_result), 50,
                                    "Search did not return <= 50 groups when used with max_groups=50")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_search_groups_150_max110(self):
        """
        Number of groups exceeds the amount returned in a single call. Paging gets implemented. This test checks if
        GroupManager class works under paging when max results is reduced to 110 from a default 2000
        :return:
        """
        try:
            group_search_result = self.gis.groups.search(query="owner: " + self.portal_username, max_groups=110)

            print("Number of groups returned in search: " + str(len(group_search_result)))

            self.assertLessEqual(len(group_search_result), 110,
                                 "Search did not return <= 110 groups when used with max_groups=50")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End GIS module Tests**")