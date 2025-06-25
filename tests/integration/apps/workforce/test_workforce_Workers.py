# -------------------------------------------------------------------------------
# Name:        Workforce Workers tests
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
class Test_Workforce_Workers(unittest.TestCase):
    """
    Test to verify that workers can be queried, added, updated, and deleted from a project
    """

    def add_worker(self):
        self.project.workers.add(
            user_id="ar_workforce_python_api2",
            contact_number="123-456-7890",
            name="ar_workforce_python_api2",
            notes="some notes",
            title="Inspector",
        )

    def reset_project(self):
        self.project.workers.batch_delete(self.project.workers.search())

    def setup_project(self):
        self.add_worker()

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        project_name = f"Workforce-ntgrtn-tst_{uuid.uuid4().hex[:5]}"
        cls.project = create_project(project_name)

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")

    def test_search_worker(self):
        try:
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(worker.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "not_working", "Incorrect status")
            self.assertEqual(worker.notes, "some notes", "Incorrect note")
            self.assertEqual(worker.title, "Inspector", "Incorrect title")

            workers = self.project.workers.search("1=0")
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_worker(self):
        try:
            # batch update
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(worker.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "not_working", "Incorrect status")
            worker.update(status="working")
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(worker.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "working", "Incorrect status")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_worker(self):
        try:
            # batch update
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(worker.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "not_working", "Incorrect status")
            worker.status = "working"
            self.project.workers.batch_update([worker])
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(worker.name, "ar_workforce_python_api2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "working", "Incorrect status")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_worker(self):
        try:
            worker = self.project.workers.search()[0]
            worker.delete()
            workers = self.project.workers.search()
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_worker(self):
        try:
            worker = self.project.workers.search()[0]
            self.project.workers.batch_delete([worker])
            workers = self.project.workers.search()
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_worker(self):
        try:
            self.project.workers.add(
                user_id="ar_OpsDashAUITest2",
                contact_number="123-456-7890",
                name="ar_OpsDashAUITest2",
                notes="some notes",
                title="Inspector",
            )
            worker = self.project.workers.search()[-1]
            self.assertEqual(worker.user_id, "ar_OpsDashAUITest2", "Incorrect user id")
            self.assertEqual(worker.name, "ar_OpsDashAUITest2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "not_working", "Incorrect status")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_worker(self):
        try:
            worker = Worker(
                self.project,
                user_id="ar_OpsDashAUITest2",
                contact_number="123-456-7890",
                name="ar_OpsDashAUITest2",
                notes="some notes",
                title="Inspector",
            )
            self.project.workers.batch_add([worker])
            worker = self.project.workers.search()[-1]
            self.assertEqual(worker.user_id, "ar_OpsDashAUITest2", "Incorrect user id")
            self.assertEqual(worker.name, "ar_OpsDashAUITest2", "Incorrect name")
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "not_working", "Incorrect status")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()
