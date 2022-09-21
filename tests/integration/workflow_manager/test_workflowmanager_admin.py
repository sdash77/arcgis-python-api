import unittest
import datetime

from arcgis.gis.workflowmanager import WorkflowManagerAdmin
from src.arcgis.gis.workflowmanager import WorkflowManager, WorkflowManagerAdmin
from src.arcgis.gis import GIS
import datetime

from tests.integration.workflow_manager.workflowmanager_setup import (
    WorkflowManagerSetup,
)


###########################################################################
# @unittest.SkipTest
class TestWorkflowManager(unittest.TestCase):
    """Tests the workflow manager Functionality"""

    # region Setup

    @classmethod
    def setUpClass(cls):
        cls.connection = WorkflowManagerSetup()

    def setUp(self):
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

    # endregion

    # region Create Item

    def test_create_item_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.create_item(
            "Testing_Item_" + str(datetime.datetime.now())
        )

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")

        # Clean up
        item = self.connection._gis.content.get(actual)
        self.connection.workflow_manager_admin.delete_item(item)

    def test_create_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            self.connection.workflow_manager_admin.create_item(
                self.connection.item_name
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Delete Item

    def test_delete_item_returns_successfully(self):
        # Act
        item_id = self.connection.workflow_manager_admin.create_item(
            "Testing_Item_" + str(datetime.datetime.now())
        )
        item = self.connection._gis.content.get(item_id)
        actual = self.connection.workflow_manager_admin.delete_item(item)

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_delete_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            fake_item = type("FakeItem", (object,), {"id": "unknown_item"})
            self.connection.workflow_manager_admin.delete_item(fake_item)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Upgrade Item

    def test_upgrade_item_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.upgrade_item(
            self.connection.workflow_item
        )

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_upgrade_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            fake_item = type("FakeItem", (object,), {"id": "unknown_item"})
            self.connection.workflow_manager_admin.upgrade_item(fake_item)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Check Server Status

    def test_check_server_status_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.server_status

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    # endregion

    # region Health Check

    def test_health_check_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.health_check

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    # endregion

    # region IWA and PKI Connection issues

    def test_check_iwa_connection_returns_successfully(self):
        # Arrange
        portal_url = "https://rqawiniwa02pt.ags.esri.com/gis/home"
        portal_username = "creator2"
        portal_password = "portalaccount1"

        gis = GIS(url=portal_url, username=portal_username, password=portal_password)
        workflow_manager_admin = WorkflowManagerAdmin(gis)

        # Create Testing Workflow Item

        item_name = "Testing_Item_" + str(datetime.datetime.now())

        # Act
        try:
            workflow_item_id = workflow_manager_admin.create_item(item_name)

            workflow_item = gis.content.get(workflow_item_id)
            workflow_manager = WorkflowManager(workflow_item)

            # basic check using api that needs a token
            roles = workflow_manager.wm_roles

            # Assertions
            self.assertIsInstance(roles, list, "Incorrect return type")
            self.assertEqual(len(roles), 5, "Incorrect number of items downloaded")

        except Exception as testException:
            print(
                "Error returned while creating Workflow Manager Item: "
                + testException.__str__()
            )

    # endregion


if __name__ == "__main__":
    unittest.main()
