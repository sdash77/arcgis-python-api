import datetime
from tests.integration.config import QALAB_ROOT_PATH
from configparser import ConfigParser
from arcgis.gis.workflowmanager import WorkflowManager, WorkflowManagerAdmin
from arcgis.gis import GIS
from utils.decorators import integration_test


###########################################################################
# @unittest.SkipTest
@integration_test
class WorkflowManagerSetup:
    """Tests the workflow manager Functionality"""

    # region Setup

    def __init__(self, override_gis: GIS = None):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        custom_testing = False

        _conf_reader = ConfigParser()
        credential_path = QALAB_ROOT_PATH + r"\wmx\config.ini"
        _conf_reader.read(credential_path, "UTF-8")

        if custom_testing:
            self.portal_url = _conf_reader["credentials"]["custom"]
            self.portal_username = _conf_reader["credentials"]["username"]
            self.portal_password = _conf_reader["credentials"]["password"]
            self.item_name = "Testing Item"
            self.workflow_item_id = "77f3d5c6ab9d46d3ba17967c32b9b00e"

            self._gis = override_gis or GIS(
                url=self.portal_url,
                username=self.portal_username,
                password=self.portal_password,
                verify_cert=False,
            )

            self.workflow_item = self._gis.content.get(self.workflow_item_id)
            self.workflow_manager = WorkflowManager(self.workflow_item)
            self.workflow_manager_admin = WorkflowManagerAdmin(self._gis)

        else:
            self.portal_url = _conf_reader["credentials"]["url"]
            self.portal_username = _conf_reader["credentials"]["username"]
            self.portal_password = _conf_reader["credentials"]["password"]

            self._gis = override_gis or GIS(
                url=self.portal_url,
                username=self.portal_username,
                password=self.portal_password,
                verify_cert=False,
            )
            self.workflow_manager_admin = WorkflowManagerAdmin(self._gis)

            # Create Testing Workflow Item
            self.item_name = "PythonAPI_Tests_" + str(datetime.datetime.now())

            try:
                self.workflow_item_id = self.workflow_manager_admin.create_item(
                    self.item_name
                )

                self.workflow_item = self._gis.content.get(self.workflow_item_id)
                self.workflow_manager = WorkflowManager(self.workflow_item)
            except Exception as testException:
                print(
                    "Error returned while creating Workflow Manager Item: "
                    + testException.__str__()
                )

    def remove_item(self):
        try:
            item = self._gis.content.get(self.workflow_item_id)
            self.workflow_manager_admin.delete_item(item)

        except Exception as testException:
            print(
                "Error returned while removing Workflow Manager Item at the end of testing: "
                + testException.__str__()
            )
