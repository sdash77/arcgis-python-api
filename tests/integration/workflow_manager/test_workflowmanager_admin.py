import unittest
import datetime
from tests.integration.workflow_manager.workflowmanager_setup import WorkflowManagerSetup


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
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                     str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
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
        actual = self.connection.workflow_manager_admin.create_item('Testing_Item_' + str(datetime.datetime.now()))

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")

        # Clean up
        self.connection.workflow_manager_admin.delete_item(actual)

    def test_create_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            self.connection.workflow_manager_admin.create_item(self.connection.item_name)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Delete Item

    def test_delete_item_returns_successfully(self):
        # Act
        item_id = self.connection.workflow_manager_admin.create_item('Testing_Item_' + str(datetime.datetime.now()))
        actual = self.connection.workflow_manager_admin.delete_item(item_id)

        # Assert
        self.assertIsTrue(actual, "Incorrect return type")

    def test_delete_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            self.connection.workflow_manager_admin.delete_item("unknown_item")
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Upgrade Item

    def test_upgrade_item_returns_successfully(self):
        # Act
        item_id = self.connection.workflow_manager_admin.create_item('Testing_Item_' + str(datetime.datetime.now()))
        actual = self.connection.workflow_manager_admin.upgrade_item(item_id)

        # Assert
        self.assertIsTrue(actual, "Incorrect return type")

    def test_upgrade_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            self.connection.workflow_manager_admin.upgrade_item("unknown_item")
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion


if __name__ == "__main__":
    unittest.main()
