# -------------------------------------------------------------------------------
# Name:        Workforce Assignment Types tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import datetime
import unittest
import uuid
from arcgis.apps.workforce import *
from arcgis.apps.workforce.managers import *
from utils.decorators import integration_test, profiles


@profiles.admin_agol
@integration_test
class Test_Workforce_Assignment_Types(unittest.TestCase):
    """
    Test to verify that assignments types can be fetched, updated, added, deleted
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        project_name = f"Workforce-ntgrtn-tst_{uuid.uuid4().hex[:5]}"
        cls.project = create_project(project_name)

    def setup_project(self):
        self.project.assignment_types.add(name="Inspection")

    def reset_project(self):
        self.project.assignment_types.batch_delete(
            self.project.assignment_types.search()
        )

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()

    def test_attachment_type_manager(self):
        try:
            assignment_types = self.project.assignment_types.search()
            self.assertIsInstance(assignment_types[0], AssignmentType, "Incorrect type")
            self.assertEqual(assignment_types[0].name, "Inspection", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment_type(self):
        try:
            self.project.assignment_types.add(name="Removal")
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_assignment_type(self):
        try:
            assignment_type = AssignmentType(self.project, name="Removal")
            self.project.assignment_types.batch_add([assignment_type])
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.delete()
            assignment_types = self.project.assignment_types.search()
            self.assertEqual(
                len(assignment_types), 0, "Incorrect number of assignment types"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            self.project.assignment_types.batch_delete([assignment_type])
            self.assertEqual(
                len(self.project.assignment_types.search()),
                0,
                "Incorrect number of assignment types",
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.name = "Repair"
            self.project.assignment_types.batch_update([assignment_type])
            assignment_type = self.project.assignment_types.search()[0]
            self.assertEqual(
                assignment_type.name, "Repair", "Incorrect assignment type"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.update(name="Repair")
            assignment_type = self.project.assignment_types.search()[0]
            self.assertEqual(
                assignment_type.name, "Repair", "Incorrect assignment type"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_assignment_type_validation(self):
        try:
            with self.assertRaises(ValidationError):
                self.project.assignment_types.add()

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")


if __name__ == "__main__":
    unittest.main()
