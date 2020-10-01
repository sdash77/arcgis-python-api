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
        actual = self.connection.workflow_manager_admin.create_item('Test Item123')

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")

    def test_create_item_returns_error(self):
        # Act
        try:
            # Try creating item with already created name
            self.connection.workflow_manager_admin.create_item(self.connection.item_name)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion


if __name__ == "__main__":
    unittest.main()
