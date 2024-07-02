# -------------------------------------------------------------------------------
# Name:        Workforce Project class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
from arcgis.auth.tools import LazyLoader
arcgismapping = LazyLoader("arcgis.map")
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
    from arcgis.gis import GIS, Group, User, Item
    from arcgis.features import Feature, FeatureLayer
    from arcgis.apps.workforce import *
    from arcgis.apps.workforce.managers import *
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check

# TestModule
@unittest.skipIf(
    module_skip, "Precondition check failed. Skipping tests in Workforce Project"
)
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

from utils.decorators import integration_test


@integration_test
class Test_Workforce_Project(unittest.TestCase):
    """
    Test to verify that a workforce project has the correct properties and methods
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, "UTF-8")

        cls.portal_url = _conf_reader["workforce_ago"]["url"]
        cls.portal_username = _conf_reader["workforce_ago"]["publisher_user"]
        cls.portal_password = _conf_reader["workforce_ago"]["publisher_password"]
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        t = datetime.datetime.now()
        cls.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        cls.project = create_project(cls.time_stamp)
        cls.project_id = cls.project.id

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_Project class")

    def setUp(self):
        self.setup_project()
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def setup_project(self):
        project = Project(self.gis.content.get(self.project_id))
        project.update(summary="Python API Regression Test")

    def test_get_project(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            self.assertIsNotNone(project, "Cannot access project")

            self.assertIsInstance(
                project.assignment_types, AssignmentTypeManager, "Incorrect type"
            )
            self.assertIsInstance(
                project.assignments, AssignmentManager, "Incorrect type"
            )
            self.assertIsInstance(project.assignments_item, Item, "Incorrect type")

            self.assertIsInstance(
                project.assignments_layer, FeatureLayer, "Incorrect type"
            )
            self.assertIsInstance(project.assignments_layer_url, str, "Incorrect type")

            self.assertIsInstance(project.dispatcher_web_map_id, str, "Incorrect type")
            self.assertIsInstance(project.dispatcher_webmap, arcgismapping.Map, "Incorrect type")
            self.assertIsInstance(
                project.dispatchers, DispatcherManager, "Incorrect type"
            )
            self.assertIsInstance(project.dispatchers_item, Item, "Incorrect type")
            self.assertIsInstance(
                project.dispatchers_layer, FeatureLayer, "Incorrect type"
            )
            self.assertIsInstance(project.dispatchers_layer_url, str, "Incorrect type")

            self.assertIsInstance(project.group, Group, "Incorrect type")
            self.assertIsInstance(project.group_id, str, "Incorrect type")

            self.assertIsInstance(project.id, str, "Incorrect type")
            self.assertEqual(project.id, self.project_id, "Incorrect project id")

            self.assertIsInstance(project.owner, User, "Incorrect type")
            self.assertIsInstance(project.owner_user_id, str, "Incorrect type")
            self.assertEqual(
                project.owner_user_id, "ar_workforce_python_api", "Incorrect owner name"
            )

            self.assertIsInstance(project.summary, str, "Incorrect type")
            self.assertEqual(
                project.summary, "Python API Regression Test", "Incorrect summary"
            )
            self.assertIsInstance(project.title, str, "Incorrect type")
            self.assertIsInstance(project.version, str, "Incorrect type")

            self.assertIsInstance(project.worker_web_map_id, str, "Incorrect type")
            self.assertIsInstance(project.worker_webmap, arcgismapping.Map, "Incorrect type")
            self.assertIsInstance(project.workers, WorkerManager, "Incorrect type")
            self.assertIsInstance(project.workers_item, Item, "Incorrect type")
            self.assertIsInstance(project.workers_layer, FeatureLayer, "Incorrect type")
            self.assertIsInstance(project.workers_layer_url, str, "Incorrect type")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_project(self):
        try:
            project = Project(self.gis.content.get(self.project_id))
            project.update(summary="A new summary")
            self.assertEqual(project.summary, "A new summary")
            # Re-get project to verify changes on server
            project2 = Project(self.gis.content.get(self.project_id))
            self.assertEqual(project2.summary, "A new summary")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()
