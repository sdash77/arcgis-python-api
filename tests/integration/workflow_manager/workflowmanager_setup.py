from src.arcgis.gis.workflowmanager import WorkflowManager, WorkflowManagerAdmin
from src.arcgis.gis import GIS
import datetime

from tests.integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser


###########################################################################
# @unittest.SkipTest
class WorkflowManagerSetup:
    """Tests the workflow manager Functionality"""

    # region Setup

    def __init__(self):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        custom_testing = False

        if custom_testing:
            self.portal_url = 'https://ps0010644.esri.com/portal'
            self.portal_username = 'admin'
            self.portal_password = 'esri.agp'
            self.item_name = 'Testing Item'
            self.workflow_item_id = 'e12fce06ff2641b68d7ec739267ed974'

            self._gis = GIS(url=self.portal_url,
                            username=self.portal_username,
                            password=self.portal_password,
                            verify_cert=False)

            self.workflow_item = self._gis.content.get(self.workflow_item_id)
            self.workflow_manager = WorkflowManager(self.workflow_item)
            self.workflow_manager_admin = WorkflowManagerAdmin(self._gis)

        else:
            _conf_reader = ConfigParser()
            _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

            self.portal_url = _conf_reader['portalhostds']['url']
            self.portal_username = _conf_reader['portalhostds']['creator_user']
            self.portal_password = _conf_reader['portalhostds']['creator_password']

            self._gis = GIS(url=self.portal_url,
                            username=self.portal_username,
                            password=self.portal_password,
                            verify_cert=False)
            self.workflow_manager_admin = WorkflowManagerAdmin(self._gis)

            # Create Testing Workflow Item
            self.item_name = 'Testing_Item_' + str(datetime.datetime.now())

            try:
                self.workflow_item_id = self.workflow_manager_admin.create_item(self.item_name)

                self.workflow_item = self._gis.content.get(self.workflow_item_id)
                self.workflow_manager = WorkflowManager(self.workflow_item)
            except Exception as testException:
                # TODO fix to account for bad setup
                print("Error returned while creating Workflow Manager Item: " + testException.__str__())

