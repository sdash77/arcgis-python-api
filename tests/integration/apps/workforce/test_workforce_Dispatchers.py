# -------------------------------------------------------------------------------
# Name:        Workforce Dispatchers tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import datetime
import unittest

from arcgis.auth.tools._util import detect_proxy

PROXY = detect_proxy(True)

from arcgis.apps.workforce import *
from arcgis.apps.workforce.managers import *

from utils.decorators import integration_test, profiles


@profiles.admin_agol
@integration_test
class Test_Workforce_Dispatchers(unittest.TestCase):
    """
    Test to check that dispatchers can be queried, added, updated, and deleted
    """

    def add_dispatcher(self):
        dispatcher = self.project.dispatchers.search(
            where="name = 'ar_workforce_python_api5'"
        )
        if not dispatcher:
            self.project.dispatchers.add(
                user_id="ar_workforce_python_api5",
                contact_number="123-456-7890",
                name="ar_workforce_python_api5",
            )

    def reset_project(self):
        pass
        # self.project.dispatchers.batch_delete(
        #     self.project.dispatchers.search(
        #         where="{} <> '{}'".format(
        #             self.project._dispatcher_schema.user_id,
        #             "ar_workforce_python_api",
        #         )
        #     )
        # )

    def setup_project(self):
        self.add_dispatcher()

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        t = datetime.datetime.now()
        cls.time_stamp = str.format(
            "Workforce-Ntgrtn-tst: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        cls.project = create_project(cls.time_stamp)

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Workforce-Ntgrtn-tst: {0}_{1}_{2}_{3}_{4}_{5}",
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
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_search_dispatcher(self):
        try:
            # 1=1 which is the default, appears to trigger some CDN caching, using 2>1 avoids this
            dispatchers = self.project.dispatchers.search("2>1")
            self.assertEqual(len(dispatchers), 2, "Incorrect number of dispatchers")

            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api5",
                )
            )[0]
            self.assertEqual(
                dispatcher.user_id,
                "ar_workforce_python_api5",
                "Incorrect user id",
            )
            self.assertEqual(
                dispatcher.name,
                "ar_workforce_python_api tester",
                "Incorrect name",
            )
            self.assertEqual(
                dispatcher.contact_number, None, "Incorrect contact number"
            )

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )
            self.assertEqual(len(dispatchers), 1, "Incorrect number of dispatchers")
            self.assertEqual(
                dispatchers[0].user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.get(
                user_id="ar_workforce_python_api2"
            )
            self.assertEqual(
                dispatcher.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(
                dispatcher.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                dispatcher.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            dispatcher.update(name="tester2")
            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )[0]
            self.assertEqual(dispatcher.name, "tester2", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.get(
                user_id="ar_workforce_python_api2"
            )
            self.assertEqual(
                dispatcher.user_id,
                "ar_workforce_python_api2",
                "Incorrect user id",
            )
            self.assertEqual(
                dispatcher.name, "ar_workforce_python_api2", "Incorrect name"
            )
            self.assertEqual(
                dispatcher.contact_number,
                "123-456-7890",
                "Incorrect contact number",
            )
            dispatcher.name = "tester2"
            self.project.dispatchers.batch_update([dispatcher])
            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )[0]
            self.assertEqual(dispatcher.name, "tester2", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )[0]
            dispatcher.delete()

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )
            self.assertEqual(len(dispatchers), 0, "Incorrect number of dispatchers")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_dispatcher(self):
        try:
            dispatcher = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )[0]
            self.project.dispatchers.batch_delete([dispatcher])

            dispatchers = self.project.dispatchers.search(
                "{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_workforce_python_api2",
                )
            )
            self.assertEqual(len(dispatchers), 0, "Incorrect number of dispatchers")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_dispatcher(self):
        try:

            self.project.dispatchers.add(name="test", user_id="ar_OpsDashAUITest2")
            dispatcher = self.project.dispatchers.search(
                where="{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_OpsDashAUITest2",
                )
            )[0]
            self.assertEqual(
                dispatcher.user_id, "ar_OpsDashAUITest2", "Incorrect user id"
            )
            self.assertEqual(dispatcher.name, "test", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_dispatcher(self):
        try:

            dispatcher = Dispatcher(
                self.project, name="test", user_id="ar_OpsDashAUITest2"
            )
            self.project.dispatchers.batch_add([dispatcher])
            dispatcher = self.project.dispatchers.search(
                where="{} = '{}'".format(
                    self.project._dispatcher_schema.user_id,
                    "ar_OpsDashAUITest2",
                )
            )[0]
            self.assertEqual(
                dispatcher.user_id, "ar_OpsDashAUITest2", "Incorrect user id"
            )
            self.assertEqual(dispatcher.name, "test", "Incorrect name")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_validate_dispatcher(self):
        try:
            # invalid user id
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="some_name_that_does_not_exist", name="test"
                )
            # no name
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="ar_OpsDashAUITest2",
                )
            # duplicate user id
            with self.assertRaises(ValidationError):
                self.project.dispatchers.add(
                    user_id="ar_workforce_python_api", name="test"
                )
            # remove project owner
            with self.assertRaises(ValidationError):
                self.project.dispatchers.search()[0].delete()

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


# TestModule
def tearDownModule():
    print("**End Workforce DispatcherManager Tests**")


if __name__ == "__main__":
    unittest.main()
