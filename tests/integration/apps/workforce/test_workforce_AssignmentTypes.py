# -------------------------------------------------------------------------------
# Name:        Workforce Assignment Types tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import datetime
import unittest

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

    def setup_project(self):
        self.project.assignment_types.add(name="Inspection")

    def reset_project(self):
        self.project.assignment_types.batch_delete(
            self.project.assignment_types.search()
        )

    def setUp(self):
        # reset project for each test
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_"
        self.reset_project()
        self.setup_project()

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

    def test_attachment_type_manager(self):
        try:
            assignment_types = self.project.assignment_types.search()
            self.assertIsInstance(assignment_types[0], AssignmentType, "Incorrect type")
            self.assertEqual(assignment_types[0].name, "Inspection", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment_type(self):
        try:
            self.project.assignment_types.add(name="Removal")
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_assignment_type(self):
        try:
            assignment_type = AssignmentType(self.project, name="Removal")
            self.project.assignment_types.batch_add([assignment_type])
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_assignment_type_validation(self):
        try:
            with self.assertRaises(ValidationError):
                self.project.assignment_types.add()

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")


if __name__ == "__main__":
    unittest.main()
