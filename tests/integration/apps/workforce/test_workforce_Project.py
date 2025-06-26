# -------------------------------------------------------------------------------
# Name:        Workforce Project class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import uuid

from arcgis.auth.tools import LazyLoader

arcgismapping = LazyLoader("arcgis.map")

from arcgis.gis import Group, User, Item
from arcgis.features import FeatureLayer
from arcgis.apps.workforce import *
from arcgis.apps.workforce.managers import *

from utils.decorators import integration_test, profiles


@profiles.admin_agol
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
        project_name = f"Workforce-ntgrtn-tst_{uuid.uuid4().hex[:5]}"
        cls.project = create_project(project_name)
        cls.project_id = cls.project.id

    def setUp(self):
        self.setup_project()

    @classmethod
    def tearDownClass(cls):
        cls.project.delete()

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
            self.assertIsInstance(
                project.dispatcher_webmap, arcgismapping.Map, "Incorrect type"
            )
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
                project.owner_user_id, "ArcGISPyAPIBot", "Incorrect owner name"
            )

            self.assertIsInstance(project.summary, str, "Incorrect type")
            self.assertEqual(
                project.summary, "Python API Regression Test", "Incorrect summary"
            )
            self.assertIsInstance(project.title, str, "Incorrect type")
            self.assertIsInstance(project.version, str, "Incorrect type")

            self.assertIsInstance(project.worker_web_map_id, str, "Incorrect type")
            self.assertIsInstance(
                project.worker_webmap, arcgismapping.Map, "Incorrect type"
            )
            self.assertIsInstance(project.workers, WorkerManager, "Incorrect type")
            self.assertIsInstance(project.workers_item, Item, "Incorrect type")
            self.assertIsInstance(project.workers_layer, FeatureLayer, "Incorrect type")
            self.assertIsInstance(project.workers_layer_url, str, "Incorrect type")

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

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()
