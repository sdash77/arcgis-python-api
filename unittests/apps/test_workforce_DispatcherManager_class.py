#-------------------------------------------------------------------------------
# Name:        Workforce DispatcherManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from dino_utils.dino_precondition_checks import PreconditionChecks
from dino_utils.dino_configs import DinoConfigs
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
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Workforce_Dispatcher_Manager(unittest.TestCase):
    """
    Test to check that dispatchers can be queried, added, updated, and deleted
    """
    # portal_url = ""
    # portal_username = ""
    # portal_password = ""

    def add_assignment(self):
        assignment = Assignment(self.project)
        assignment.assignment_type = self.project.assignment_types.get(name="Inspection")
        assignment.status = "UNASSIGNED"
        assignment.geometry = {"x": 123, "y": 456}
        assignment.location = "there"
        assignment.description = "Do some work"
        assignment.dispatcher = self.project.dispatchers.get(user_id='ar_workforce_python_api')
        self.project.assignments.batch_add([assignment])

    def add_assignment_types(self):
        # Add an assignment type
        self.project.assignment_types.add(name="Removal")
        self.project.assignment_types.add(name="Inspection")

    def add_dispatcher(self):
        self.project.dispatchers.add(user_id='ar_workforce_python_api2',
                                     contact_number='123-456-7890',
                                     name='ar_workforce_python_api2')

    def add_worker(self):
        self.project.workers.add(user_id='ar_workforce_python_api2', contact_number='123-456-7890', name='ar_workforce_python_api2')

    def reset_project(self):
        self.project.assignments.batch_delete(self.project.assignments.search())
        self.project.assignment_types.batch_delete(self.project.assignment_types.search())
        self.project.tracks.batch_delete(self.project.tracks.search())
        self.project.workers.batch_delete(self.project.workers.search())
        self.project.dispatchers.batch_delete(self.project.dispatchers.search(where="{} <> '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api')))

    def setup_project(self):
        self.add_assignment_types()
        self.add_worker()
        self.add_dispatcher()
        self.add_assignment()


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
        cls.project_id = "4b50c61e471f40628ab9dd32b19e0b75"
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        cls.project = Project(cls.gis.content.get(cls.project_id))
        # delete assignments and assignment types
        cls.dispatcher_manager = cls.project.dispatchers


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
        print("\n==================================================================")

    def test_search_dispatcher(self):
        try:
            dispatcher = self.dispatcher_manager.search()[0]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api", "Incorrect user id")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api tester", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, "123-456-7890", "Incorrect contact number")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_dispatcher(self):
        try:
            # batch update
            dispatcher = self.dispatcher_manager.search()[1]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, "123-456-7890", "Incorrect contact number")
            dispatcher.name = "tester1"
            self.dispatcher_manager.batch_update([dispatcher])
            dispatcher = self.dispatcher_manager.search()[1]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.assertEqual(dispatcher.name, "tester1", "Incorrect name")
            self.assertEqual(dispatcher.contact_number, "123-456-7890", "Incorrect contact number")
            # single update
            dispatcher.update(name="tester2")
            dispatcher = self.dispatcher_manager.search()[1]
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
            dispatcher = self.dispatcher_manager.search("{} = '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api2'))[0]
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api2", "Incorrect user id")
            self.dispatcher_manager.batch_delete([dispatcher])
            dispatchers = self.dispatcher_manager.search()
            self.assertEqual(len(dispatchers), 1, "Incorrect number of dispatchers")


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