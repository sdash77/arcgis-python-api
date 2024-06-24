# -------------------------------------------------------------------------------
# Name:        Workforce Workers tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import (
    PreconditionChecks,
)
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime

# region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()
from arcgis.auth.tools._util import detect_proxy

PROXY = detect_proxy(True)
if r1 & r2:
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise (exit())

# Import the module after Precondition checks pass
try:
    from arcgis.gis import GIS
    from arcgis.apps.workforce import *
    from arcgis.apps.workforce._schemas import *
    from arcgis.apps.workforce.managers import *
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check

# TestModule
@unittest.skipIf(
    module_skip,
    "Precondition check failed. Skipping tests in Workforce Workers",
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
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, "UTF-8")

        cls.portal_url = _conf_reader["workforce_ago"]["url"]
        cls.portal_username = _conf_reader["workforce_ago"]["publisher_user"]
        cls.portal_password = _conf_reader["workforce_ago"][
            "publisher_password"
        ]
        cls.gis = GIS(
            cls.portal_url,
            cls.portal_username,
            cls.portal_password,
            verify_cert=False,
            proxy=PROXY,
        )
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

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print(
            "=================================================================="
        )
        print("Beginning tests in Test_Workforce_WorkerManager class")

    def setUp(self):
        # reset project for each test
        self.reset_project()
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
        print(
            "------------------------------------------------------------------\n"
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print(
            "\n=================================================================="
        )

    def test_search_worker(self):
        try:
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(
                worker.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(
                worker.status, "not_working", "Incorrect status"
            )
            self.assertEqual(worker.notes, "some notes", "Incorrect note")
            self.assertEqual(worker.title, "Inspector", "Incorrect title")

            workers = self.project.workers.search("1=0")
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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
            self.assertEqual(
                worker.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(
                worker.status, "not_working", "Incorrect status"
            )
            worker.update(status="working")
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(
                worker.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "working", "Incorrect status")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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
            self.assertEqual(
                worker.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(
                worker.status, "not_working", "Incorrect status"
            )
            worker.status = "working"
            self.project.workers.batch_update([worker])
            worker = self.project.workers.search()[0]
            self.assertEqual(
                worker.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(
                worker.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(worker.status, "working", "Incorrect status")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_worker(self):
        try:
            worker = self.project.workers.search()[0]
            worker.delete()
            workers = self.project.workers.search()
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_worker(self):
        try:
            worker = self.project.workers.search()[0]
            self.project.workers.batch_delete([worker])
            workers = self.project.workers.search()
            self.assertEqual(len(workers), 0, "Incorrect number of workers")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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
            self.assertEqual(
                worker.user_id, "ar_OpsDashAUITest2", "Incorrect user id"
            )
            self.assertEqual(
                worker.name, "ar_OpsDashAUITest2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(
                worker.status, "not_working", "Incorrect status"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

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
            self.assertEqual(
                worker.user_id, "ar_OpsDashAUITest2", "Incorrect user id"
            )
            self.assertEqual(
                worker.name, "ar_OpsDashAUITest2", "Incorrect name"
            )
            self.assertEqual(
                worker.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            self.assertEqual(
                worker.status, "not_working", "Incorrect status"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())



if __name__ == "__main__":
    unittest.main()