#-------------------------------------------------------------------------------
# Name:        Workforce Project class tests
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
    from arcgis.gis import GIS, Group, User, Item
    from arcgis.features import Feature, FeatureLayer
    from arcgis.mapping import WebMap
    from arcgis.apps.workforce import *
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

class Test_Workforce_Project(unittest.TestCase):
    """
    Test to verify that a workforce project has the correct properties and methods
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

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.project_id = "9bc9bac7fbf748e4a128da7684fda0a5"
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_Project class")

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

    def test_get_project(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            self.assertIsNotNone(project, "Cannot sign access project")
            self.assertEqual(project.title, "Project 1", "Incorrect title")
            self.assertEqual(project.id, self.project_id, "Incorrect id")
            self.assertIsInstance(project.assignments, AssignmentManager, "Incorrect type")
            self.assertIsInstance(project.assignment_types, AssignmentTypeManager, "Incorrect type")
            self.assertIsInstance(project.workers, WorkerManager, "Incorrect type")
            self.assertIsInstance(project.dispatchers, DispatcherManager, "Incorrect type")
            self.assertIsInstance(project.tracks, TrackManager, "Incorrect type")
            self.assertIsInstance(project.dispatcher_webmap, WebMap, "Incorrect type")
            self.assertIsInstance(project.worker_webmap, WebMap, "Incorrect type")
            self.assertIsInstance(project.group, Group, "Incorrect type")
            self.assertEqual(project.group.title, "Project 1", "Incorrect group title")
            self.assertIsInstance(project.owner, User, "Incorrect type")
            self.assertEqual(project.owner.firstName, "ar_workforce_python_api", "Incorrect owner name")
            self.assertIsInstance(project.assignments_layer, FeatureLayer, "Incorrect type")
            self.assertIn(project.assignments_layer.properties.name, "Assignments", "Incorrect layer name")
            self.assertIsInstance(project.dispatchers_layer, FeatureLayer, "Incorrect type")
            self.assertIn(project.dispatchers_layer.properties.name, "Dispatchers", "Incorrect layer name")
            self.assertIsInstance(project.workers_layer, FeatureLayer, "Incorrect type")
            self.assertIn(project.workers_layer.properties.name, "Workers", "Incorrect layer name")
            self.assertIsInstance(project.tracks_layer, FeatureLayer, "Incorrect type")
            self.assertIn(project.tracks_layer.properties.name, "Location Tracking", "Incorrect layer name")
            self.assertIsInstance(project.assignments_item, Item, "Incorrect type")
            self.assertIsInstance(project.dispatchers_item, Item, "Incorrect type")
            self.assertIsInstance(project.workers_item, Item, "Incorrect type")
            self.assertIsInstance(project.tracks_item, Item, "Incorrect type")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_get_worker(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            worker = project.workers.get(object_id=1)
            self.assertEqual(worker.name, "ar_workforce_python_api tester", "Incorrect worker name")
            self.assertEqual(worker.contact_number, "123-456-7890", "Incorrect contact number")
            self.assertEqual(worker.notes, "Test Inspector.", "Incorrect notes")
            self.assertEqual(worker.id, 1, "Incorrect id")
            self.assertEqual(worker.status, "not_working", "Incorrect status")
            self.assertEqual(worker.title, "Inspector", "Incorrect title")
            self.assertEqual(worker.user_id, "ar_workforce_python_api", "Incorrect user id")
            self.assertIsInstance(worker.feature, Feature, "Incorrect type")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_get_dispatcher(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            dispatcher = project.dispatchers.get(object_id=1)
            self.assertEqual(dispatcher.name, "ar_workforce_python_api tester", "Incorrect dispatcher name")
            self.assertEqual(dispatcher.user_id, "ar_workforce_python_api", "Incorrect user id")
            self.assertEqual(dispatcher.id, 1, "Incorrect id")
            self.assertEqual(dispatcher.contact_number, "098-765-4321", "Incorrect contact number")
            self.assertEqual(dispatcher.name, "ar_workforce_python_api tester", "Incorrect name")
            self.assertIsInstance(dispatcher.feature, Feature, "Incorrect type")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_get_assignment(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            assignment = project.assignments.get(object_id=1)
            self.assertEqual(assignment.description, "Perform and inspection here.", "Incorrect inspection description")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


#TestModule
def tearDownModule():
    print("**End Workforce Project Tests**")