#-------------------------------------------------------------------------------
# Name:        Workforce Dispatchers tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import random

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
    from arcgis.gis import GIS, Group, User
    from arcgis.features import Feature, FeatureLayer
    from arcgis.mapping import WebMap
    from arcgis.apps.workforce import *
    from arcgis.apps.workforce._schemas import *
    from arcgis.apps.workforce.managers import *
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Dispatchers")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Workforce_Dispatchers(unittest.TestCase):
    """
    Test to check that dispatchers can be queried, added, updated, and deleted
    """

    def add_dispatcher(self):
        self.project.dispatchers.add(user_id='ar_workforce_python_api2',
                                     contact_number='123-456-7890',
                                     name='ar_workforce_python_api2')

    def reset_project(self):
        self.project.dispatchers.batch_delete(self.project.dispatchers.search(where="{} <> '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api')))

    def setup_project(self):
        self.add_dispatcher()


    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        t = datetime.datetime.now()
        cls.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                    str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        cls.project = create_project(cls.time_stamp)


        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_DispatcherManager class")

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()
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
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_search_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search()[0]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api", "Incorrect user id")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api tester", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, None, "Incorrect contact number")

            dispatcher2 = self.project.dispatchers.search()[1]
            self.assertEqual(dispatcher2.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.assertEqual(dispatcher2.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(dispatcher2.contact_number, "123-456-7890", "Incorrect contact number")

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))
            self.assertEqual(len(dispatchers), 1, "Incorrect number of dispatchers")
            self.assertEqual(dispatchers[0].user_id, "ar_workforce_python_api2", "Incorrect user id")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search()[1]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, "123-456-7890", "Incorrect contact number")
            dispatcher.update(name="tester2")
            dispatcher = self.project.dispatchers.search()[1]
            self.assertEqual(dispatcher.name, "tester2", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search()[1]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, "123-456-7890", "Incorrect contact number")
            dispatcher.name="tester2"
            self.project.dispatchers.batch_update([dispatcher])
            dispatcher = self.project.dispatchers.search()[1]
            self.assertEqual(dispatcher.name, "tester2", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search("{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))[0]
            dispatcher.delete()

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))
            self.assertEqual(len(dispatchers), 0, "Incorrect number of dispatchers")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))[0]
            self.project.dispatchers.batch_delete([dispatcher])

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))
            self.assertEqual(len(dispatchers), 0, "Incorrect number of dispatchers")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_dispatcher(self):
        try:

            self.project.dispatchers.add(
                name="test",
                user_id="ar_OpsDashAUITest"
            )
            dispatcher = self.project.dispatchers.search()[-1]
            self.assertEqual(dispatcher.user_id, "ar_OpsDashAUITest", "Incorrect user id")
            self.assertEqual(dispatcher.name, "test", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_dispatcher(self):
        try:

            dispatcher = Dispatcher(
                self.project,
                name="test",
                user_id="ar_OpsDashAUITest"
            )
            self.project.dispatchers.batch_add([dispatcher])
            dispatcher = self.project.dispatchers.search()[-1]
            self.assertEqual(dispatcher.user_id, "ar_OpsDashAUITest", "Incorrect user id")
            self.assertEqual(dispatcher.name, "test", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_validate_dispatcher(self):
        try:
            # invalid user id
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="some_name_that_does_not_exist",
                    name="test"
                )
            # no name
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="ar_OpsDashAUITest",
                )
            # duplicate user id
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="ar_workforce_python_api2",
                    name="test"
                )
            # remove project owner
            with self.assertRaises(ValidationError):
                self.project.dispatchers.search()[0].delete()

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


#TestModule
def tearDownModule():
    print("**End Workforce DispatcherManager Tests**")