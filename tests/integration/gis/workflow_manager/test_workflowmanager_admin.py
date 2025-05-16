import json
import os
import tempfile
import unittest

from arcgis.gis.workflowmanager import (
    WorkflowManager,
    WorkflowManagerAdmin,
    Notification,
    ItemExecution,
)
from arcgis.gis import GIS
import datetime
import re
import uuid

from utils.decorators import integration_test
from . import workflowmanager_setup


###########################################################################
# @unittest.SkipTest
@integration_test
class TestWorkflowManager(unittest.TestCase):
    """Tests the workflow manager Functionality"""

    # region Setup

    @classmethod
    def setUpClass(cls):
        cls.connection = workflowmanager_setup.WorkflowManagerSetup()

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
        cls.connection.remove_item()
        print("\n==================================================================")

    # endregion

    # region Create Item

    def test_create_item_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.create_item(
            "Testing_Create_Item_" + str(datetime.datetime.now())
        )

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")

        # Clean up
        item = self.connection._gis.content.get(actual)
        self.connection.workflow_manager_admin.delete_item(item)

    # endregion

    # region Delete Item

    def test_delete_item_returns_successfully(self):
        # Act
        item_id = self.connection.workflow_manager_admin.create_item(
            "Testing_Delete_Item_" + str(datetime.datetime.now())
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

    # region Import Item

    def test_import_item_returns_successfully(self):
        # Act
        item = self.connection.workflow_item
        filepath = self.connection.workflow_manager_admin.export_item(item)

        item_id_two = self.connection.workflow_manager_admin.create_item(
            "Testing_Import_Item2_" + str(datetime.datetime.now())
        )

        item_two = self.connection._gis.content.get(item_id_two)
        try:
            actual = self.connection.workflow_manager_admin.import_item(
                item_two, filepath
            )

            # Assert
            self.assertTrue(actual, "Incorrect return type")
        finally:
            self.connection.workflow_manager_admin.delete_item(item_two)

    def test_import_item__with_passphrase_returns_successfully(self):
        # Act
        passphrase = "test phrase"
        item = self.connection.workflow_item
        filepath = self.connection.workflow_manager_admin.export_item(
            item, passphrase=passphrase
        )

        item_id_two = self.connection.workflow_manager_admin.create_item(
            "Testing_Import_Item4_" + str(datetime.datetime.now())
        )

        item_two = self.connection._gis.content.get(item_id_two)
        try:
            actual = self.connection.workflow_manager_admin.import_item(
                item_two, filepath, passphrase=passphrase
            )

            # Assert
            self.assertTrue(actual, "Incorrect return type")
        finally:
            self.connection.workflow_manager_admin.delete_item(item_two)

    def test_import_item_async_returns_successfully(self):
        # Act
        item = self.connection.workflow_item
        filepath = self.connection.workflow_manager_admin.export_item(item)

        item_id_two = self.connection.workflow_manager_admin.create_item(
            "Testing_Import_Item2_" + str(datetime.datetime.now())
        )
        item_two = self.connection._gis.content.get(item_id_two)
        try:
            importItemExec = self.connection.workflow_manager_admin.import_item(
                item_two, filepath, run_async=True
            )

            # Assert
            self.assertTrue(importItemExec.running(), "Import is not still running")
            result = importItemExec.result()
            self.assertIsInstance(result, Notification, "Result is not a Notification")
            self.assertTrue(importItemExec.done(), "Import is not done")
        finally:
            self.connection.workflow_manager_admin.delete_item(item_two)

    # endregion

    # region Export Item

    def test_export_item_returns_successfully(self):
        # Act
        item = self.connection.workflow_item
        actual = self.connection.workflow_manager_admin.export_item(item)
        export_size = os.stat(actual).st_size

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue(
            "workflow_configuration" in actual, "Did not return a temporary file path"
        )
        self.assertGreater(export_size, 0, "Downloaded file size is not greater than 0")

    def test_export_item_with_save_path_returns_successfully(self):
        # Act
        item = self.connection.workflow_item

        with tempfile.TemporaryDirectory() as temp_dir:
            directory = temp_dir
            actual = self.connection.workflow_manager_admin.export_item(
                item, save_path=temp_dir
            )
            export_size = os.stat(actual).st_size

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue(
            directory in actual,
            f"Output {actual} did not exist within specified save_path {directory}",
        )
        self.assertTrue(
            "workflow_configuration" in actual,
            "Output did not contain expected filename",
        )
        self.assertGreater(export_size, 0, "Downloaded file size is not greater than 0")

    def test_export_item_async_returns_successfully(self):
        # Act
        item = self.connection.workflow_item

        actual = self.connection.workflow_manager_admin.export_item(
            item, run_async=True
        )
        self.assertTrue(actual.running(), "Export is not running")
        res = actual.result()
        # Assert
        self.assertIsInstance(actual, ItemExecution, "Incorrect return type")
        self.assertIsInstance(res, Notification, "Incorrect return type")
        self.assertTrue(
            os.path.isfile(actual.export_location), "Did not download wmc correctly."
        )

    def test_export_item_async_with_save_path_returns_successfully(self):
        # Act
        item = self.connection.workflow_item
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = temp_dir
            exportItemExec = self.connection.workflow_manager_admin.export_item(
                item, run_async=True, save_path=temp_dir
            )
            self.assertIsInstance(
                exportItemExec, ItemExecution, "Incorrect return type"
            )
            exportItemExec.result()
            actual = exportItemExec.export_location
            export_size = os.stat(actual).st_size

        # Assert
        self.assertIsNotNone(exportItemExec.export_id)
        # Verify exported file
        self.assertTrue(
            directory in actual,
            f"Output {actual} did not exist within specified save_path {directory}",
        )
        self.assertTrue(
            "workflow_configuration" in actual,
            "Output did not contain expected filename",
        )
        self.assertGreater(export_size, 0, "Downloaded file size is not greater than 0")
        # Verify no exported mapping file
        self.assertIsNone(exportItemExec.export_mapping_location)

    def test_export_item_async_with_export_mapping_file_returns_successfully(self):
        # Act
        item = self.connection.workflow_item
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = temp_dir
            exportItemExec = self.connection.workflow_manager_admin.export_item(
                item, run_async=True, save_path=temp_dir, export_mapping=True
            )
            self.assertIsInstance(
                exportItemExec, ItemExecution, "Incorrect return type"
            )
            exportItemExec.result()
            exported_file = exportItemExec.export_location  # config file
            export_size = os.stat(exported_file).st_size
            exported_mapping_file = (
                exportItemExec.export_mapping_location
            )  # mapping file
            export_mapping_size = os.stat(exported_mapping_file).st_size

        # Assert
        self.assertIsNotNone(exportItemExec.export_id)
        # Verify exported file
        self.assertTrue(
            directory in exported_file,
            f"Output {exported_file} did not exist within specified save_path {directory}",
        )
        self.assertTrue(
            "workflow_configuration" in exported_file,
            "Output did not contain expected filename",
        )
        self.assertGreater(
            export_size, 0, "Downloaded configuration file size is not greater than 0"
        )
        # Verify exported mapping file
        self.assertTrue(
            directory in exported_mapping_file,
            f"Output {exported_mapping_file} did not exist within specified save_path {directory}",
        )
        self.assertTrue(
            "workflow_mapping" in exported_mapping_file,
            "Output did not contain expected filename",
        )
        self.assertGreater(
            export_mapping_size, 0, "Downloaded mapping file size is not greater than 0"
        )

    def test_export_item_with_passphrase_returns_successfully(self):
        item = self.connection.workflow_item
        actual = self.connection.workflow_manager_admin.export_item(
            item, passphrase="test phrase"
        )

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue(
            "workflow_configuration" in actual, "Did not return a temporary file path"
        )

    def test_export_item_with_specific_job_templates_returns_successfully(self):
        # Act
        item_id = self.connection.workflow_manager_admin.create_item(
            "Testing_Export_Item3_" + str(datetime.datetime.now())
        )

        item = self.connection._gis.content.get(item_id)
        try:
            wm = WorkflowManager(item)
            uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
            diagram_id = wm.create_diagram(
                name="Test New Diagram123 " + uniqueness,
                display_grid=True,
                description="Test Description",
                active=True,
                annotations=[
                    {
                        "position": "0,0,100,250",
                        "color": "130, 202, 237",
                        "outlineColor": "130, 202, 237",
                        "labelColor": "black",
                        "text": "test annotations",
                    }
                ],
                data_sources=[
                    {"name": "dsource", "url": "string", "sourceType": "string"}
                ],
                steps=[
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Start and end of a workflow",
                        "helpText": "Start/End help text",
                        "helpUrl": "Start/End help url",
                        "id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                        "labelColor": "black",
                        "name": "Start/End",
                        "outlineColor": "130, 202, 237",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "21bff5ee-1586-a635-30ea" "-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    }
                ],
            )

            uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

            name = "Testing Template  " + uniqueness
            table_name = "testing_table_" + uniqueness
            template_id = uniqueness[0:22]

            diagrams = self.connection.workflow_manager.diagrams
            diagram = {}
            for gram in diagrams:
                if gram.diagram_name == "Introduction to Workflow Manager":
                    diagram = gram
                    break

            template_id = wm.create_job_template(
                name=name,
                id=template_id,
                diagram_id=diagram.diagram_id,
                diagram_name=diagram.diagram_name,
                priority="high",
                category="Functional Tests",
                job_duration=5,
                assigned_to=self.connection.portal_username,
                default_due_date="2020-04-02T13:25:50Z",
                default_start_date="2020-04-02T13:25:50Z",
                start_date_type="CreationDate",
                assigned_type="Unassigned",
                description="Test Test test",
                default_description="Test Test123",
                state="Active",
                last_updated_by="Abbie Admin",
                last_updated_date="2020-04-02T13:25:50Z",
                extended_property_table_definitions=[
                    {
                        "tableName": table_name,
                        "tableAlias": table_name,
                        "tableOrder": 0,
                        "relationshipType": "OneToOne",
                        "extendedPropertyDefinitions": [
                            {
                                "propertyOrder": 0,
                                "visible": True,
                                "propertyName": "prop1",
                                "editable": True,
                                "dataType": "String",
                                "propertyAlias": "prop1",
                                "required": True,
                                "fieldLength": 50,
                            },
                            {
                                "propertyOrder": 1,
                                "visible": True,
                                "propertyName": "prop2",
                                "editable": True,
                                "dataType": "String",
                                "propertyAlias": "prop2",
                                "required": True,
                                "fieldLength": 50,
                            },
                            {
                                "propertyOrder": 2,
                                "visible": True,
                                "propertyName": "string",
                                "editable": True,
                                "domain": {
                                    "type": "codedValue",
                                    "codedValues": [
                                        {"code": "123", "name": "123"},
                                        {"code": "456", "name": "456"},
                                    ],
                                    "range": ["string"],
                                },
                                "dataType": "String",
                                "propertyAlias": "string",
                                "required": True,
                                "fieldLength": 50,
                            },
                        ],
                    }
                ],
            )

            actual = self.connection.workflow_manager_admin.export_item(
                item, [template_id], [diagram_id, diagram.diagram_id], False
            )

            # Assert
            self.assertIsInstance(actual, str, "Incorrect return type")
            self.assertTrue(
                "workflow_configuration" in actual,
                "Did not return a temporary file path",
            )
        finally:
            self.connection.workflow_manager_admin.delete_item(item)

    # endregion

    # region Check Server Status

    def test_check_server_status_returns_successfully(self):
        # Act
        actual = self.connection.workflow_manager_admin.server_status

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_check_server_status_uses_private_url(self):
        gis_source = self.connection._gis
        public_url = gis_source._url
        referer = ""
        token_resp = gis_source._con.post(
            gis_source._con._token_url,
            {
                "username": gis_source.users.me.username,
                "password": self.connection.portal_password,
                "referer": json.dumps(referer),
                "expiration": 1440,
                "f": "json",
            },
            add_token=False,
        ).get("token", None)
        if token_resp is None:
            raise Exception(
                "Could not authenticate, please verify `your_enterprise_profile` exists on the system."
            )
        del gis_source

        with tempfile.TemporaryDirectory() as d:
            token = json.dumps(
                {
                    "token": f"{token_resp}",
                    "referer": "",
                    "privatePortalUrl": public_url,
                    "publicPortalUrl": public_url,
                    "expiration": 20160,
                }
            )
            f = open(os.path.join(d, ".nbauth.json"), "w")
            f.write(token)
            f.close()
            del f
            os.getenv
            with unittest.mock.patch.dict(
                "os.environ",
                {"NB_AUTH_FILE": os.path.join(d, ".nbauth.json")},
                clear=True,
            ):
                gis = GIS("HOME")
                local_connection = workflowmanager_setup.WorkflowManagerSetup(gis)
                self.assertTrue(
                    local_connection._gis._use_private_url_only,
                    "Portal was not mocked to use private url only",
                )

                actual = local_connection.workflow_manager_admin.server_status

                self.assertTrue(actual, "Incorrect return type")
                self.assertTrue(
                    local_connection.workflow_manager_admin._url.endswith(
                        ":13443/workflow"
                    ),
                    f"{local_connection.workflow_manager_admin._url} was not a private URL",
                )

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
        portal_username = "avworld\\creator2"
        portal_password = "portalaccount1"

        gis = GIS(
            url=portal_url,
            username=portal_username,
            password=portal_password,
            verify_cert=False,
            hostname_override=portal_url.replace("https://", "")
            .replace(".ags", "")
            .split("/")[0],
        )
        workflow_manager_admin = WorkflowManagerAdmin(gis)

        # Create Testing Workflow Item

        item_name = "Testing_Item_" + str(datetime.datetime.now())

        # Act
        try:
            workflow_item_id = workflow_manager_admin.create_item(item_name)

            workflow_item = gis.content.get(workflow_item_id)
            try:
                workflow_manager = WorkflowManager(workflow_item)

                # basic check using api that needs a token
                roles = workflow_manager.wm_roles

                # Assertions
                self.assertIsInstance(roles, list, "Incorrect return type")
                self.assertEqual(len(roles), 4, "Incorrect number of items downloaded")
            finally:
                self.connection.workflow_manager_admin.delete_item(workflow_item)

        except Exception as testException:
            print(
                "Error returned while creating Workflow Manager Item: "
                + testException.__str__()
            )

    # endregion


if __name__ == "__main__":
    unittest.main()
