import threading
import unittest
import datetime
import re
import time
from pprint import pprint

import arcgis.gis.workflowmanager._workflow_manager
from arcgis.geometry import Geometry
from . import workflowmanager_setup
from arcgis.gis.workflowmanager import (
    WorkflowManager,
    WorkflowManagerAdmin,
    MessageType,
    ExecutionStatus,
    NotificationManager,
    Notification,
    JobExecution,
)
from arcgis.gis import GIS
from tests.integration.config import QALAB_ROOT_PATH
from configparser import ConfigParser
from utils.decorators import integration_test
import uuid


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

    def create_diagram(self):
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
        return self.connection.workflow_manager.create_diagram(
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
            data_sources=[{"name": "dsource", "url": "string", "sourceType": "string"}],
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
            centralized_data_references=[],
        )

    def create_diagram_with_cdr(self):
        uniqueness = uuid.uuid4().hex
        return self.connection.workflow_manager.create_diagram(
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
            data_sources=[],
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
            centralized_data_references=[
                {
                    "id": "e8e5c963-a485-4f5f-a298-dcf430f72c28",
                    "proItemName": "MyProMap",
                    "referenceType": "ProMapItem",
                }
            ],
            use_centralized_data_references=True,
        )

    def create_diagram_robust(self):
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
        d_id = uniqueness[0:22]
        return self.connection.workflow_manager.create_diagram(
            name="Test New Diagram123 " + uniqueness,
            diagram_id=d_id,
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
            data_sources=[],
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
            centralized_data_references=[
                {
                    "id": "e8e5c963-a485-4f5f-a298-dcf430f72c28",
                    "proItemName": "MyProMap",
                    "referenceType": "ProMapItem",
                }
            ],
        )

    def create_job(
        self, count=1, template_name="Introduction to Workflow Manager", job_id=None
    ):
        job_templates = self.connection.workflow_manager.job_templates
        job_template = {}
        for x in job_templates:
            if x.job_template_name == template_name:
                job_template = x

        return self.connection.workflow_manager.jobs.create(
            template=job_template.job_template_id,
            count=count,
            name="Test New Job123",
            start="2020-04-02T13:25:50Z",
            end="2020-04-02T13:25:50Z",
            priority="High",
            description="hopefully this works...",
            owner=self.connection.portal_username,
            assigned=self.connection.portal_username,
            complete=42,
            notes="testing notes",
            parent="",
            job_id=job_id,
        )

    def create_job_template(self):
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

        return self.connection.workflow_manager.create_job_template(
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

    def create_job_robust(self, location=None):
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        template_name = "Testing Template  " + uniqueness
        table_name = "testing_table_" + uniqueness

        self.create_job_template_robust(
            template_name=template_name, table_name=table_name
        )

        job_templates = self.connection.workflow_manager.job_templates
        job_template = {}
        for x in job_templates:
            if x.job_template_name == template_name:
                job_template = x

        if location is None:
            location = {
                "geometryType": "Polygon",
                "geometry": '{"rings":[[[-6848757.734349992,3330625.6782390587],[-2256822.369376309,'
                "6774572.424655061],[-2935181.886149995,1973920.9766344912],[-6848757.734349992,"
                '3330625.6782390587]]],"spatialReference":{"latestWkid":3857,"wkid":102100}}',
            }

        return self.connection.workflow_manager.jobs.create(
            template=job_template.job_template_id,
            count=1,
            name="Test New Job123",
            start="2020-04-02T13:25:50Z",
            end="2020-04-02T13:25:50Z",
            priority="High",
            description="hopefully this works...",
            owner=self.connection.portal_username,
            assigned=self.connection.portal_username,
            complete=42,
            notes="testing notes",
            parent="",
            location=location,
            extended_properties=[
                {"identifier": table_name + ".prop1", "value": "newly_created123"},
                {"identifier": table_name + ".prop2", "value": "newly_created456"},
                {"identifier": table_name + ".prop4", "value": "1"},
            ],
            related_properties=[
                {
                    "tableName": "related_props_table123",
                    "entries": [
                        {
                            "properties": [
                                {"propertyName": "rel_prop1", "value": "string"}
                            ]
                        }
                    ],
                }
            ],
        )

    def create_job_template_robust(self, template_name, table_name):
        name = template_name
        table_name = table_name

        diagrams = self.connection.workflow_manager.diagrams
        diagram = {}
        for gram in diagrams:
            if gram.diagram_name == "Introduction to Workflow Manager":
                diagram = gram
                break

        return self.connection.workflow_manager.create_job_template(
            name=name,
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
                            "propertyName": "prop4",
                            "editable": True,
                            "domain": {
                                "type": "codedValue",
                                "codedValues": [
                                    {"code": "1", "name": "Uno"},
                                    {"code": "2", "name": "Dos"},
                                ],
                                "range": ["string"],
                            },
                            "dataType": "Integer",
                            "propertyAlias": "prop4",
                            "required": True,
                            "fieldLength": 50,
                        },
                    ],
                }
            ],
        )

    # endregion

    # region Users

    def test_get_users(self):
        # Act
        users = self.connection.workflow_manager.users

        # Assertions
        self.assertIsInstance(users, list, "Incorrect return type")
        self.assertEqual(len(users), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(users[0], dict, "Incorrect type")

    def test_get_valid_users(self):
        # Arrange
        valid_user = {
            "email": "admin@mydomain.com",
            "fullName": "Administrator",
            "username": "admin",
        }

        # Act
        users = self.connection.workflow_manager.users

        # Assert
        self.assertIsInstance(users, list, "Incorrect return type")
        self.assertEqual(len(users), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(users[0], dict, "Incorrect type")

    def test_get_specific_user(self):
        # Arrange
        users = self.connection.workflow_manager.users
        default_user = {}
        for user in users:
            if user["username"] == self.connection.portal_username:
                default_user = user
                break

        # Act
        user = self.connection.workflow_manager.user(default_user["username"])

        # Assert
        self.assertEqual(
            default_user["username"], user.username, "Incorrect role returned"
        )

    def test_get_specific_user_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.role(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region WM_Roles

    def test_get_wm_roles(self):
        # Act
        roles = self.connection.workflow_manager.wm_roles

        # Assertions
        self.assertIsInstance(roles, list, "Incorrect return type")
        self.assertEqual(len(roles), 5, "Incorrect number of items downloaded")

    def test_get_valid_wm_roles(self):
        # Arrange
        valid_role = {
            "description": "Role with basic privileges to manage jobs. Privileges "
            "assigned are assign job to group, assign job to individual, "
            "update holds, attachments and queries",
            "privileges": [
                "jobAssignGroup",
                "jobUpdateHolds",
                "jobUpdateAttachments",
                "queryUpdate",
                "jobAssignIndividual",
                "viewWorkPage",
                "viewCreatePanel",
                "viewDetailsPanelAttachments",
                "viewDetailsPanelProperties",
                "viewDetailsPanelLocation",
            ],
            "role_name": "Manage Jobs - Basic",
        }

        # Act
        roles = self.connection.workflow_manager.wm_roles
        found_role = [x for x in roles if x.role_name == valid_role["role_name"]]

        # Assert
        self.assertIsInstance(roles, list, "Incorrect return type")
        self.assertEqual(len(roles), 5, "Incorrect number of items downloaded")
        self.assertTrue(found_role, "Does not contain default role")

    def test_get_specific_wm_role(self):
        # Arrange
        test_name = "Manage Jobs - Basic"

        # Act
        role = self.connection.workflow_manager.wm_role(test_name)

        # Assert
        self.assertEqual(
            "Manage Jobs - Basic", role.role_name, "Incorrect role returned"
        )

    def test_get_specific_wm_role_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.wm_role(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_create_wm_role_successfully_returns(self):
        # Arrange

        # Act
        actual = self.connection.workflow_manager.create_wm_role(
            name="Test New Role",
            description="Test Description",
            privileges=["adminAdvanced", "jobCreate", "jobDelete"],
        )

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_create_wm_role_returns_error(self):
        # Arrange

        # Act
        try:
            self.connection.workflow_manager.create_wm_role(
                name="Test New Role",
                description="Test Description",
                privileges=["fakePrivilege123", "jobCreate", "jobDelete"],
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_delete_wm_role_successfully_returns(self):
        # Arrange

        created = self.connection.workflow_manager.create_wm_role(
            name="Test New Role",
            description="Test Description",
            privileges=["adminAdvanced", "jobCreate", "jobDelete"],
        )
        self.assertTrue(created, "Incorrect return type")

        # Act
        deleted = self.connection.workflow_manager.delete_wm_role("Test New Role")

        self.assertTrue(deleted, "Incorrect return type")

    def test_delete_wm_role_returns_error(self):
        # Act
        deleted = self.connection.workflow_manager.delete_wm_role("Incorrect")

        try:
            self.assertTrue(deleted, "Incorrect return type")
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Assignable

    def test_get_assignable_users(self):
        # Act
        assignable_users = self.connection.workflow_manager.assignable_users

        # Assertions
        self.assertIsInstance(assignable_users, list, "Incorrect return type")
        self.assertEqual(
            len(assignable_users), 1, "Incorrect number of items downloaded"
        )
        self.assertIsInstance(assignable_users[0], dict, "Incorrect type")

    def test_get_valid_assignable_users(self):
        # Arrange
        valid_assignable_user = {
            "email": "admin@mydomain.com",
            "fullName": "Administrator",
            "username": "admin",
        }

        # Act
        assignable_users = self.connection.workflow_manager.assignable_users

        # Assert
        self.assertIsInstance(assignable_users, list, "Incorrect return type")
        self.assertEqual(
            len(assignable_users), 1, "Incorrect number of items downloaded"
        )
        self.assertIsInstance(assignable_users[0], dict, "Incorrect type")

    def test_get_assignable_groups(self):
        # Act
        assignable_groups = self.connection.workflow_manager.assignable_groups

        # Assertions
        self.assertIsInstance(assignable_groups, list, "Incorrect return type")
        self.assertEqual(
            len(assignable_groups), 1, "Incorrect number of items downloaded"
        )
        self.assertIsInstance(assignable_groups[0], dict, "Incorrect type")

    def test_get_valid_assignable_groups(self):
        # Arrange
        default_group_name = "Workflow Manager Admin " + self.connection.item_name

        # Act
        groups = self.connection.workflow_manager.assignable_groups
        found_group = [x for x in groups if x["title"] == default_group_name]
        pprint(groups)
        print(default_group_name)

        # Assert
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")
        self.assertTrue(found_group, "Does not contain default group")

    # endregion

    # region Groups

    def test_get_groups(self):
        # Act
        groups = self.connection.workflow_manager.groups

        # Assertions
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")

    def test_get_valid_groups(self):
        # Arrange
        default_group_name = "Workflow Manager Admin " + self.connection.item_name

        # Act
        groups = self.connection.workflow_manager.groups
        found_group = [x for x in groups if x["title"] == default_group_name]

        # Assert
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")
        self.assertTrue(found_group, "Does not contain default group")

    def test_get_specific_group(self):
        # Arrange
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        # Act
        # returns object with roles assigned to group
        specific_group = self.connection.workflow_manager.group(group["id"])
        has_group = "Workflow Administrator" in specific_group.roles

        # Assert
        self.assertTrue(has_group, "Incorrect group with included roles returned")

    def test_get_specific_group_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.group(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_update_group(self):
        # Arrange
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        add_roles = {"adds": {"roles": ["Workflow Designer"]}}
        delete_roles = {"deletes": {"roles": ["Workflow Designer"]}}

        # Act
        self.connection.workflow_manager.update_group(group["id"], add_roles)
        specific_group = self.connection.workflow_manager.group(group["id"])
        has_role = "Workflow Designer" in specific_group.roles

        self.connection.workflow_manager.update_group(group["id"], delete_roles)
        specific_group = self.connection.workflow_manager.group(group["id"])
        does_not_have_role = "Workflow Designer" not in specific_group.roles

        # Assert
        self.assertTrue(has_role, "Incorrectly updated group")
        self.assertTrue(does_not_have_role, "Incorrect updated group")

    def test_update_group_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.update_group(test_id, {})
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Searches
    def test_get_searches_default(self):
        # Act
        searches = self.connection.workflow_manager.searches()

        # Assertions
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertIsInstance(searches[0], dict, "Incorrect type")

    def test_get_searches_standard(self):
        # Act
        searches = self.connection.workflow_manager.searches("Standard")

        # Assertions
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertIsInstance(searches[0], dict, "Incorrect type")

    def test_get_searches_charts(self):
        # Act
        searches = self.connection.workflow_manager.searches("Chart")

        # Assertions
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertIsInstance(searches[0], dict, "Incorrect type")

    def test_get_searches_all(self):
        # Act
        searches = self.connection.workflow_manager.searches("All")

        # Assertions
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertIsInstance(searches[0], dict, "Incorrect type")

    def test_get_valid_searches(self):
        # Arrange
        valid_search = {
            "searchId": "rrUF60TFQCe2K0vtgSsYpA",
            "name": "My Jobs",
            "definition": {
                "q": "\"assignedType='User' AND closed=0 AND assignedTo='\" + $currentUser + \"' \"",
                "fields": [
                    "assignedTo",
                    "jobName",
                    "dueDate",
                    "jobTemplateName",
                    "currentStep",
                    "priority",
                    "jobStatus",
                ],
                "displayNames": [
                    "Assigned To",
                    "Name",
                    "Due",
                    "Type",
                    "Step",
                    "Priority",
                    "Status",
                ],
                "sortFields": [
                    {"field": "jobName", "sortOrder": "Asc"},
                    {"field": "priority", "sortOrder": "Asc"},
                ],
                "start": 0,
                "num": 50,
            },
            "searchType": "Standard",
            "sortIndex": 1000,
        }

        valid_chart = {
            "searchId": "KPHh4-l1SaKRkO8eZLoeEA",
            "name": "Job Type Chart",
            "definition": {
                "fields": ["job_template_name"],
                "displayNames": ["Type"],
                "sortFields": [{"field": "job_template_name", "sortOrder": "Asc"}],
                "start": 0,
                "num": 50,
            },
            "searchType": "Chart",
            "colorRamp": "Default",
            "sortIndex": 2000,
        }

        # Act
        searches = self.connection.workflow_manager.searches("All")
        has_search = valid_search in searches
        has_chart = valid_chart in searches

        # Assert
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertIsInstance(searches[0], dict, "Incorrect type")
        self.assertTrue(has_search, "Does not contain default search")
        self.assertTrue(has_chart, "Does not contain default chart")

    def test_search_jobs_successfully_returns_with_default_fields(self):
        # Arrange
        diagram_id = "abcde12345"
        user_query = (
            "assignedType='User' AND closed=0 AND diagramId='" + diagram_id + "' "
        )
        expected = {
            "q": "assigned_type='User' AND closed=0 AND diagram='abcde12345' ",
            "fields": [
                {"name": "jobName", "fieldType": "String"},
                {"name": "priority", "fieldType": "String"},
                {"name": "dueDate", "fieldType": "DateTime"},
                {"name": "currentStep", "fieldType": "String"},
            ],
            "results": [],
            "start": 0,
            "next_start": -1,
            "num": 0,
        }

        expected_job_list = []

        # Act
        # No fields selected so expect default fields of jobName, priority, dueDate and currentStep
        actual = self.connection.workflow_manager.jobs.search(query=user_query)
        job_list = actual.get("results")

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(expected, actual, "Incorrect search returned")
        self.assertEqual(job_list, expected_job_list, "Incorrect search returned")

    def test_search_jobs_successfully_returns_with_selected_fields(self):
        # Arrange
        diagram_id = "abcde12345"
        user_query = (
            "assignedType='User' AND closed=0 AND diagramId='" + diagram_id + "' "
        )
        expected = {
            "q": "assigned_type='User' AND closed=0 AND diagram='abcde12345' ",
            "fields": [
                {"name": "jobId", "fieldType": "String"},
                {"name": "diagramVersion", "fieldType": "Integer"},
            ],
            "results": [],
            "start": 0,
            "next_start": -1,
            "num": 0,
        }

        expected_job_list = []

        # Act
        actual = self.connection.workflow_manager.jobs.search(
            query=user_query, fields=["jobId", "diagramVersion"]
        )
        job_list = actual.get("results")

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(actual, expected, "Incorrect search returned")
        self.assertEqual(job_list, expected_job_list, "Incorrect search returned")

    def test_search_jobs_returns_error(self):
        # Arrange
        diagram_id = "abcde12345"
        user_query = (
            "assignedType='User' AND closed=0 AND diagram_id='" + diagram_id + "' "
        )

        # Act
        try:
            self.connection.workflow_manager.search_jobs(
                query=user_query, fields=["jobId", "diagramVersion"]
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # region Create Saved Search

    def test_create_saved_search(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        searchid = uniqueness[0:22]

        # Act
        actual = self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "q": "closed=0",
                "start": 0,
                "num": 50,
                "fields": [
                    "assignedTo",
                    "jobName",
                    "currentStep",
                    "jobTemplateName",
                    "priority",
                    "dueDate",
                    "jobStatus",
                ],
                "displayNames": [
                    "Assigned To",
                    "Name",
                    "Current Step",
                    "Type",
                    "Priority",
                    "Due Date",
                    "Status",
                ],
                "sortFields": [
                    {"field": "jobName", "sortOrder": "Asc"},
                    {"field": "priority", "sortOrder": "Asc"},
                ],
            },
            search_type="Standard",
            sort_index=5000,
            search_id=searchid,
        )

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(actual, searchid, "Incorrect return type")

    def test_create_saved_search_chart(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        searchid = uniqueness[0:22]

        # Act
        actual = self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "start": 0,
                "fields": ["job_status"],
                "displayNames": ["Status"],
                "sortFields": [{"field": "job_status", "sortOrder": "Asc"}],
            },
            search_type="Chart",
            color_ramp="Flower Field Inverse",
            sort_index=2000,
            search_id=searchid,
        )

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(actual, searchid, "Incorrect return type")

    # endregion

    # region Delete Saved Search

    def test_delete_saved_search(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        searchid = uniqueness[0:22]

        # Act
        search = self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "q": "closed=0",
                "start": 0,
                "num": 50,
                "fields": [
                    "assignedTo",
                    "jobName",
                    "currentStep",
                    "jobTemplateName",
                    "priority",
                    "dueDate",
                    "jobStatus",
                ],
                "displayNames": [
                    "Assigned To",
                    "Name",
                    "Current Step",
                    "Type",
                    "Priority",
                    "Due Date",
                    "Status",
                ],
                "sortFields": [
                    {"field": "jobName", "sortOrder": "Asc"},
                    {"field": "priority", "sortOrder": "Asc"},
                ],
            },
            search_type="Standard",
            sort_index=5000,
            search_id=searchid,
        )

        actual = self.connection.workflow_manager.saved_searches.delete(search)

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")

    def test_delete_saved_search_returns_search_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.saved_searches.delete(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Update Saved Search

    def test_update_saved_search(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        searchid = uniqueness[0:22]

        # Act
        self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "start": 0,
                "fields": ["job_status"],
                "displayNames": ["Status"],
                "sortFields": [{"field": "job_status", "sortOrder": "Asc"}],
            },
            search_type="Chart",
            color_ramp="Flower Field Inverse",
            sort_index=2000,
            search_id=searchid,
        )

        search_lst = self.connection.workflow_manager.searches("All")
        search = [x for x in search_lst if x["searchId"] == searchid][0]

        search["colorRamp"] = "Default"
        search["name"] = "Updated search  " + uniqueness

        actual = self.connection.workflow_manager.saved_searches.update(search)

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertTrue(actual, "Incorrectly updated search")

    # endregion

    # region Share Searches

    def test_share_details_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        search_id = uniqueness[0:22]
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        search = self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "q": "closed=0",
                "start": 0,
                "num": 50,
                "fields": [
                    "assignedTo",
                    "jobName",
                    "currentStep",
                    "jobTemplateName",
                    "priority",
                    "dueDate",
                    "jobStatus",
                ],
                "displayNames": [
                    "Assigned To",
                    "Name",
                    "Current Step",
                    "Type",
                    "Priority",
                    "Due Date",
                    "Status",
                ],
                "sortFields": [
                    {"field": "jobName", "sortOrder": "Asc"},
                    {"field": "priority", "sortOrder": "Asc"},
                ],
            },
            search_type="Standard",
            sort_index=5000,
            search_id=search_id,
        )

        # Act
        actual = self.connection.workflow_manager.saved_searches.share_details(search)

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertEqual(actual, [], "Incorrect return type")

        self.connection.workflow_manager.saved_searches.share(search, [group["id"]])

        actual_two = self.connection.workflow_manager.saved_searches.share_details(
            search
        )

        self.assertIsInstance(actual_two, list, "Incorrect return type")
        self.assertEqual(actual_two, [group["id"]], "Incorrect return type")

    def test_share_saved_search_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        search_id = uniqueness[0:22]
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        search = self.connection.workflow_manager.saved_searches.create(
            name=name,
            definition={
                "q": "closed=0",
                "start": 0,
                "num": 50,
                "fields": [
                    "assignedTo",
                    "jobName",
                    "currentStep",
                    "jobTemplateName",
                    "priority",
                    "dueDate",
                    "jobStatus",
                ],
                "displayNames": [
                    "Assigned To",
                    "Name",
                    "Current Step",
                    "Type",
                    "Priority",
                    "Due Date",
                    "Status",
                ],
                "sortFields": [
                    {"field": "jobName", "sortOrder": "Asc"},
                    {"field": "priority", "sortOrder": "Asc"},
                ],
            },
            search_type="Standard",
            sort_index=5000,
            search_id=search_id,
        )

        # Act
        actual = self.connection.workflow_manager.saved_searches.share(
            search, [group["id"]]
        )

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertEqual(actual, True, "Incorrect return type")

    # endregion

    # endregion

    # region Statistics

    def test_job_statistics_successfully_returns(self):
        # Arrange
        self.create_job()
        diagram_id = "99o2QTePTqq-BHRHK_Aeag"
        user_query = "diagramId='" + diagram_id + "' "

        # Act
        actual = self.connection.workflow_manager.jobs.statistics(
            query=user_query, group_by="assignedTo"
        )

        # Assert
        self.assertTrue(actual["total"] > 0, "Incorrect return type")
        self.assertEqual(actual["group_by"], "assignedTo", "Incorrect return type")
        self.assertIsInstance(actual["grouped_values"], list, "Incorrect return type")

    def test_job_statistics_successfully_returns_zero_results(self):
        # Arrange
        self.create_job()
        diagram_id = "WRONGID"
        user_query = "diagramId='" + diagram_id + "' "

        # Act
        actual = self.connection.workflow_manager.jobs.statistics(
            query=user_query, group_by="assignedTo"
        )

        # Assert
        self.assertTrue(actual["total"] == 0, "Incorrect return type")
        self.assertEqual(actual["group_by"], "assignedTo", "Incorrect return type")
        self.assertIsInstance(actual["grouped_values"], list, "Incorrect return type")

    def test_job_statistics_successfully_returns_zero_results(self):
        # Arrange
        self.create_job()
        diagram_id = "WRONGID"
        user_query = "diagramId='" + diagram_id + "' "

        # Act
        try:
            actual = self.connection.workflow_manager.jobs.statistics(
                query=user_query, group_by="wrong_string"
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Settings

    def test_get_valid_settings(self):
        # Arrange
        valid_settings = [
            {"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name"},
            {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
            {"propName": "smtpUsername", "value": "new_admin"},
            {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
            {"propName": "smtpPort", "value": "3113"},
            {"propName": "smtpProtocol", "value": "New Protocol"},
            {"propName": "smtpServer", "value": "New Server"},
        ]

        # Add settings
        self.connection.workflow_manager.update_settings(valid_settings)

        # Act
        settings = self.connection.workflow_manager.settings
        has_setting = [
            x
            for x in settings
            if x["propName"] == "smtpDefaultSenderDisplayName"
            and x["value"] == "Updated Name"
        ]

        # Assert
        self.assertIsInstance(settings, list, "Incorrect return type")
        self.assertTrue(has_setting, "Does not contain default settings")

    def test_get_valid_settings_without_system_settings(self):
        # Arrange
        valid_settings = [
            {"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name"},
            {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
            {"propName": "smtpUsername", "value": "new_admin"},
            {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
            {"propName": "smtpPort", "value": "3113"},
            {"propName": "smtpProtocol", "value": "New Protocol"},
            {"propName": "smtpServer", "value": "New Server"},
            {"propName": "userProp", "value": "UserSetting"},
        ]

        # Add settings
        self.connection.workflow_manager.update_settings(valid_settings)

        # Act
        settings = self.connection.workflow_manager.user_settings
        has_setting = [
            x
            for x in settings
            if x["propName"] == "smtpDefaultSenderDisplayName"
            and x["value"] == "Updated Name"
        ]
        has_user_setting = [
            x
            for x in settings
            if x["propName"] == "userProp" and x["value"] == "UserSetting"
        ]

        # Assert
        self.assertIsInstance(settings, list, "Incorrect return type")
        self.assertFalse(has_setting, "Should not contain default settings")
        self.assertTrue(has_user_setting, "Does not contain user settings")

    def test_update_settings_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
        settings = [
            {
                "propName": "smtpDefaultSenderDisplayName",
                "value": "Updated Name" + uniqueness,
            },
            {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
            {"propName": "smtpUsername", "value": "new_admin"},
            {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
            {"propName": "smtpPort", "value": "3113"},
            {"propName": "smtpProtocol", "value": "New Protocol"},
            {"propName": "smtpServer", "value": "New Server"},
        ]

        updated_settings = [
            {"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name"},
            {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
            {"propName": "smtpUsername", "value": "new_admin"},
            {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
            {"propName": "smtpPort", "value": "3113"},
            {"propName": "smtpProtocol", "value": "New Protocol"},
            {"propName": "smtpServer", "value": "New Server"},
        ]

        # Act
        actual = self.connection.workflow_manager.update_settings(
            props=updated_settings
        )

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            settings,
            self.connection.workflow_manager.settings,
            "Incorrect updated settings is returned",
        )

    def test_update_settings_returns_error(self):
        # Arrange
        updated_settings = [
            {"propName": "string", "value": "string"},
            {"propName2": "string", "value": "string"},
        ]

        # Act
        # TODO Create a bad settings update
        try:
            self.connection.workflow_manager.update_settings(props=updated_settings)

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Evaluate Arcade

    def test_evaluate_arcade_job_context(self):
        # Arrange
        expression1 = "'Job name = ' + jobName($job)"

        # Act
        # TODO Need to be able to load test data
        expected_name = "Arcade @ Tests"
        job_id = self.connection.workflow_manager.jobs.create(
            "Q5-nYVlCTBOZ4ShEdDsglA", name=expected_name
        )[0]
        result1 = self.connection.workflow_manager.evaluate_arcade(
            expression1, context_type="JobContext", context={"jobId": job_id}
        )
        result2 = self.connection.workflow_manager.evaluate_arcade(
            expression1,
            context_type="JobContext",
            context={"jobId": job_id},
            mode="URL",
        )

        # Assert
        self.assertEqual(
            f"Job name = {expected_name}",
            result1,
            "Arcade results with job context did not match",
        )
        self.assertEqual(
            f"Job name = Arcade+%40+Tests",
            result2,
            "Arcade results with URL mode did not match",
        )

    def test_evaluate_arcade_base_context(self):
        # Arrange
        expression1 = "'test ' + '123'"

        # Act
        result1 = self.connection.workflow_manager.evaluate_arcade(expression1)

        # Assert
        self.assertEqual("test 123", result1, "Arcade results did not match")

    def test_evaluate_arcade_returns_error(self):
        # Act
        expression1 = "'test '"

        try:
            # TODO add bad expression
            self.connection.workflow_manager.evaluate_arcade(
                expression1, context={"jobId": "abc123"}
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Job Tests

    # region Get Jobs

    def test_get_job(self):
        # Arrange
        test_id = self.create_job()[0]

        # Act
        job = self.connection.workflow_manager.jobs.get(test_id)

        # Assert
        self.assertEqual(job.job_id, test_id, "Incorrect number of items downloaded")

    def test_get_job_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Create Jobs

    def test_create_job_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_job()

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")

    def test_create_job_successfully_with_custom_id_returns(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
        job_id = uniqueness[0:22]

        # Act
        actual = self.create_job(job_id=job_id)
        job = self.connection.workflow_manager.job_manager.get(actual[0])

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")
        self.assertEqual(job.job_id, job_id, "Incorrect job id")

    def test_create_job_robust_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_job_robust()
        job = self.connection.workflow_manager.job_manager.get(actual[0])
        location = job.location

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")
        self.assertEqual(
            location.geometry_type, "Polygon", "Incorrect return value for location"
        )

    def test_create_multiple_job_successfully_returns(self):
        # Arrange
        job_templates = self.connection.workflow_manager.job_templates
        job_template = {}
        for x in job_templates:
            if x.job_template_name == "Introduction to Workflow Manager":
                job_template = x

        # Act
        actual = self.create_job(count=2)

        # Assert
        self.assertNotEqual(job_template, {}, "Job Template not found")
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")
        self.assertEqual(len(actual), 2, "Incorrect number of items downloaded")

    def test_create_job_returns_error_template_not_active(self):
        # Arrange

        try:
            self.create_job(template_name="Route Edits")

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_create_job_robust_location_is_geometry_class_successfully_returns(self):
        # Arrange
        new_location = {
            "geometryType": "Polygon",
            "geometry": '{"rings":[[[-6848757.734349992,3330625.6782390587],'
            "[-2256822.369376309,6774572.424655061],"
            "[-2935181.886149995,1973920.9766344912],"
            "[-6848757.734349992,3330625.6782390587]]],"
            '"spatialReference":{"latestWkid":3857,"wkid":102100}}',
        }
        geo = Geometry(new_location["geometry"])

        # Act
        actual = self.create_job_robust(location=geo)
        job = self.connection.workflow_manager.job_manager.get(actual[0])
        location = job.location

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")
        self.assertEqual(
            location.geometry_type, "Polygon", "Incorrect return value for location"
        )

    # endregion Create Jobs

    # region Update Jobs

    def test_update_job_successfully_returns(self):
        # Arrange
        job_id = self.create_job()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        a = job.location
        job.priority = "Updated"

        # Act
        actual = self.connection.workflow_manager.jobs.update(job_id, vars(job))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update"
        )

    def test_update_job_with_extended_properties_successfully_returns(self):
        # Arrange
        job_id = self.create_job_robust()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.priority = "Updated"
        delattr(job, "related_properties")
        delattr(job, "extended_properties")

        # Act
        actual = self.connection.workflow_manager.jobs.update(job_id, vars(job))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update"
        )

    def test_update_job_with_updated_extended_properties_successfully_returns(self):
        # Arrange
        job_id = self.create_job_robust()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.priority = "Updated"

        table_name = job.extended_properties[0]["tableName"]
        job.extended_properties = [
            {"identifier": table_name + ".prop1", "value": "updated_123"},
            {"identifier": table_name + ".prop2", "value": "updated_456"},
        ]

        # Act
        actual = self.connection.workflow_manager.jobs.update(job_id, vars(job))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update"
        )

    def test_update_job_with_updated_extended_properties_with_domain_successfully_returns(
        self,
    ):
        # Arrange
        job_id = self.create_job_robust()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.priority = "Updated"

        table_name = job.extended_properties[0]["tableName"]
        job.extended_properties = [
            {"identifier": table_name + ".prop1", "value": "updated_123"},
            {"identifier": table_name + ".prop2", "value": "updated_456"},
            {"identifier": table_name + ".prop4", "value": "2"},
        ]

        # Act
        actual = self.connection.workflow_manager.jobs.update(job_id, vars(job))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update"
        )

    def test_update_job_with_allow_running_step_id_successfully_returns(self):
        # Arrange
        job_id = self.create_job_robust()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.priority = "Updated"
        delattr(job, "related_properties")
        delattr(job, "extended_properties")

        # Act
        actual = self.connection.workflow_manager.jobs.update(
            job_id, vars(job), "123456"
        )

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update"
        )

    def test_update_job_returns_error(self):
        # Arrange
        job_id = "abcde12345"

        updated_job_object = {"job_id": job_id, "jobName": "Standard"}

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).update(updated_job_object)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Close Jobs

    def test_close_jobs(self):
        # Arrange
        id_list = self.create_job(count=3)

        # Act
        close_jobs = self.connection.workflow_manager.jobs.close(id_list)

        # Assert
        self.assertTrue(close_jobs, "Incorrect return type")

    def test_close_jobs_returns_not_found(self):
        # Arrange
        test_id = ["bad_id_12345"]

        # Act
        try:
            self.connection.workflow_manager.jobs.close(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Reopen Jobs

    def test_reopen_jobs(self):
        # Arrange
        id_list = self.create_job(count=3)

        # Act
        close_jobs = self.connection.workflow_manager.jobs.close(id_list)
        reopen_jobs = self.connection.workflow_manager.jobs.reopen(id_list)

        # Assert
        self.assertTrue(close_jobs, "Incorrect return type")
        self.assertTrue(reopen_jobs, "Incorrect return type")

    def test_reopen_jobs_returns_not_found(self):
        # Arrange
        test_id = ["bad_id_12345"]

        # Act
        try:
            self.connection.workflow_manager.jobs.reopen(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Upgrade Jobs

    def test_upgrade_jobs(self):
        # Arrange
        id_list = self.create_job(count=3)

        # Act
        upgrade_jobs = self.connection.workflow_manager.jobs.upgrade(id_list)

        # Assert
        self.assertTrue(upgrade_jobs, "Incorrect return type")

    def test_upgrade_jobs_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.upgrade(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Delete Jobs

    def test_delete_jobs(self):
        # Arrange
        id_list = self.create_job(count=3)

        # Act
        delete_jobs = self.connection.workflow_manager.jobs.delete(id_list)

        # Assert
        self.assertTrue(delete_jobs, "Incorrect return type")

    def test_delete_jobs_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.delete(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Update Job Version

    # Disabled this test because it requires external set up to work.
    # def test_update_job_version_successfully_returns(self):
    #     # Arrange
    #     job_id = self.create_job()[0]
    #     job = self.connection.workflow_manager.jobs.get(job_id)
    #
    #
    #     # Act
    #     actual = job.set_job_version(data_source_name="Gas_Utility_Network",
    #                                  version_name="admin.ANGEL123",
    #                                  administered=True)
    #
    #     # Assert
    #     self.assertTrue(actual, "Incorrect return type")

    # endregion

    # region Job Location

    def test_get_job_location_returns_no_location_set(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {"geometry": "{}", "geometry_type": "None"}

        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(
            default_job_location["geometry_type"],
            str(job_location.geometry_type),
            "Incorrect job location returned",
        )

    def test_set_job_location_returns_true(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {"geometry": "{}", "geometry_type": "None"}
        new_location = {
            "geometryType": "Polygon",
            "geometry": '{"rings":[[[-6848757.734349992,3330625.6782390587],'
            "[-2256822.369376309,6774572.424655061],"
            "[-2935181.886149995,1973920.9766344912],"
            "[-6848757.734349992,3330625.6782390587]]],"
            '"spatialReference":{"latestWkid":3857,"wkid":102100}}',
        }
        geo = Geometry(new_location["geometry"])

        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location
        actual = self.connection.workflow_manager.jobs.set_job_location(test_id, geo)
        new_job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(
            default_job_location["geometry_type"],
            str(job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertEqual(
            new_location["geometryType"],
            str(new_job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertTrue(actual, "Did not return correct attachment")

    def test_set_job_location_polyline_returns_true(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {"geometry": "{}", "geometry_type": "None"}
        new_location = {
            "geometryType": "Polyline",
            "geometry": '{"paths":[[[-5283327.395069996,-1730934.0112043545],'
            "[1500210.4448956922,1921738.3728870638],"
            "[-10397060.1336323,4739512.983591061],"
            "[-10449247.514693994,4739512.983591061]]],"
            '"spatialReference":{"latestWkid":3857,"wkid":102100}}',
        }
        geo = Geometry(new_location["geometry"])

        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location
        actual = self.connection.workflow_manager.jobs.set_job_location(test_id, geo)
        new_job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(
            default_job_location["geometry_type"],
            str(job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertEqual(
            new_location["geometryType"],
            str(new_job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertTrue(actual, "Did not return correct attachment")

    def test_set_job_location_point_returns_true(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {"geometry": "{}", "geometry_type": "None"}
        new_location = {
            "geometryType": "Multipoint",
            "geometry": '{"spatialReference":{"latestWkid":3857,"wkid":102100},'
            '"points":[[15067267.015569989,-2983278.2826283537]]}',
        }
        geo = Geometry(new_location["geometry"])
        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location
        actual = self.connection.workflow_manager.jobs.set_job_location(test_id, geo)
        new_job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(
            default_job_location["geometry_type"],
            str(job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertEqual(
            new_location["geometryType"],
            str(new_job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertTrue(actual, "Did not return correct attachment")

    def test_set_job_location_polyline_returns_true_with_object_format(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {"geometry": "{}", "geometry_type": "None"}
        new_location = {
            "geometryType": "Polyline",
            "geometry": '{"paths":[[[-5283327.395069996,-1730934.0112043545],'
            "[1500210.4448956922,1921738.3728870638],"
            "[-10397060.1336323,4739512.983591061],"
            "[-10449247.514693994,4739512.983591061]]],"
            '"spatialReference":{"latestWkid":3857,"wkid":102100}}',
        }

        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location
        actual = self.connection.workflow_manager.jobs.set_job_location(
            test_id, new_location
        )
        new_job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(
            default_job_location["geometry_type"],
            str(job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertEqual(
            new_location["geometryType"],
            str(new_job_location.geometry_type),
            "Incorrect job location returned",
        )
        self.assertTrue(actual, "Did not return correct attachment")

    # endregion

    # region Job Attachments

    def test_job_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = "../README.md"

        # Act
        attachment = self.connection.workflow_manager.jobs.get(job_id).add_attachment(
            url
        )
        actual = self.connection.workflow_manager.jobs.get(job_id).get_attachment(
            attachment["id"]
        )

        # Arrange
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue("README.md" in actual, "Did not return correct attachment")

    def test_job_attachment_returns_error(self):
        # Arrange
        job_id = "abcde12345"
        attachment_id = "abcde12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).get_attachment(
                attachment_id
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_job_linked_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        attachments = [
            {"url": "linked text", "folder": "General", "alias": "linkedText"},
            {"url": "https://www.esri.com", "folder": "General", "alias": "webpath"},
            {
                "url": "tests//integration//README.md",
                "folder": "General",
                "alias": "filepath",
            },
        ]

        # Act
        a_list = self.connection.workflow_manager.jobs.get(
            job_id
        ).add_linked_attachment(attachments)
        job_attachments = self.connection.workflow_manager.jobs.get(job_id).attachments
        text = job_attachments[0]["alias"]
        url = job_attachments[1]["alias"]
        file_path = job_attachments[2]["alias"]

        # Arrange
        self.assertIsInstance(a_list, list, "Incorrect return type")
        self.assertEqual(text, "linkedText", "Did not return correct attachment")
        self.assertEqual(file_path, "filepath", "Did not return correct attachment")
        self.assertEqual(url, "webpath", "Did not return correct attachment")

    def test_job_linked_attachment_returns_error(self):
        # Arrange
        job_id = "abcde12345"
        attachment_id = "abcde12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).get_linked_attachment(
                attachment_id
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_add_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = "../README.md"

        # Act
        actual = self.connection.workflow_manager.jobs.get(job_id).add_attachment(url)
        has_attachment = self.connection.workflow_manager.jobs.get(
            job_id
        ).get_attachment(actual["id"])

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertTrue(has_attachment, "Attachment is not is returned from job")

    def test_add_attachment_returns_error_bad_url(self):
        # Arrange
        job_id = self.create_job()[0]

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).add_attachment("bad_id")
        except Exception as testException:
            print(testException)
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    def test_update_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = "../README.md"
        attachment = self.connection.workflow_manager.jobs.get(job_id).add_attachment(
            url
        )
        attachment_id = attachment["id"]
        alias = "Updated alias"

        # Act
        actual = self.connection.workflow_manager.jobs.get(job_id).update_attachment(
            attachment_id, alias
        )

        # Arrange
        self.assertTrue(actual, "Incorrect return type")

    def test_delete_job_attachment(self):
        # Arrange
        test_id = self.create_job()[0]
        url = "../README.md"
        attachment_id = self.connection.workflow_manager.jobs.get(
            test_id
        ).add_attachment(url)["id"]

        # Act
        actual = self.connection.workflow_manager.jobs.delete_attachment(
            test_id, attachment_id
        )

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_delete_attachment_returns_not_found(self):
        # Arrange
        test_id = self.create_job()[0]
        url = "../README.md"
        attachment_id = self.connection.workflow_manager.jobs.get(
            test_id
        ).add_attachment(url)["id"]

        # Act
        actual = self.connection.workflow_manager.jobs.delete_attachment(
            test_id, attachment_id
        )

        # Try deleting non-existing attachment
        try:
            self.connection.workflow_manager.jobs.delete_attachment(
                test_id, attachment_id
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Job History

    def test_job_history_returns_successfully(self):
        # Arrange
        test_id = self.create_job()[0]

        # Act
        actual = self.connection.workflow_manager.jobs.get(test_id).history

        # Arrange
        self.assertIsInstance(actual, dict, "Incorrect return type")

    def test_job_history_returns_error(self):
        # Arrange
        job_id = "abcde12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).history
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Update Step Assignment

    def test_update_step_assignment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        actual = self.connection.workflow_manager.jobs.get(job_id).update_step(
            step_id=step_id,
            assigned_type="User",
            assigned_to=self.connection.portal_username,
        )

        # Arrange
        self.assertTrue(actual, "Incorrect return type")

    def test_update_step_assignment_returns_error(self):
        # Arrange
        job_id = "abcde12345"
        step_id = "abcde12345"
        assignment_type = "Group"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).update_step(
                step_id=step_id, assigned_type=assignment_type, assigned_to="Unknown"
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Set Current Step

    def test_set_current_step_returns_successfully(self):
        # Arrange
        job = self.create_job()
        job_id = job[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        # Act
        actual1 = self.connection.workflow_manager.jobs.get(job_id)
        actual = actual1.set_current_step(step_id=step_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")

    def test_set_current_step_returns_error(self):
        # Arrange
        job_id = "abcde12345"
        step_id = "abcde12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).set_current_step(
                step_id=step_id
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Holds and Release Holds

    def test_simple_add_hold_returns_successfully(self):
        # Arrange
        job = self.create_job()
        job_id = job[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        # Act
        the_job = self.connection.workflow_manager.jobs.get(job_id)
        actual = the_job.add_hold(step_ids=[step_id])

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")

    def test_simple_hold_release_returns_successfully(self):
        # Arrange
        job = self.create_job()
        job_id = job[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        # Act
        the_job = self.connection.workflow_manager.jobs.get(job_id)
        actual = the_job.add_hold(step_ids=[step_id])

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")

        # Act 2
        actual = the_job.release_hold(step_ids=[step_id])

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")
        self.assertEqual(
            the_job.holds[0]["releasedBy"], "admin", "Incorrect return type"
        )

    def test_dependent_add_hold_returns_successfully(self):
        # Arrange
        job = self.create_job()
        job_id = job[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        job_2 = self.create_job()
        job_two_id = job_2[0]
        diagram_two = self.connection.workflow_manager.jobs.diagram(job_two_id)
        step_id_two = diagram_two.steps[1]["id"]

        # Act: Add a hold to job one blocked by the step from job two
        job_one = self.connection.workflow_manager.jobs.get(job_id)
        actual = job_one.add_hold(
            step_ids=[step_id],
            dependent_step_id=step_id_two,
            dependent_job_id=job_two_id,
        )

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")

    def test_dependent_release_hold_returns_successfully(self):
        # Arrange
        job = self.create_job()
        job_id = job[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        job_2 = self.create_job()
        job_two_id = job_2[0]
        diagram_two = self.connection.workflow_manager.jobs.diagram(job_two_id)
        step_id_two = diagram_two.steps[1]["id"]

        # Act: Add a hold to job one blocked by the step from job two
        job_one = self.connection.workflow_manager.jobs.get(job_id)
        actual = job_one.add_hold(
            step_ids=[step_id],
            dependent_step_id=step_id_two,
            dependent_job_id=job_two_id,
        )

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")

        # Act: Add a hold to job one blocked by the step from job two
        actual = job_one.release_hold(
            step_ids=[step_id],
            dependent_step_id=step_id_two,
            dependent_job_id=job_two_id,
        )

        the_job = self.connection.workflow_manager.jobs.get(job_id)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")
        self.assertIsNotNone(the_job.holds, "Incorrect return type")
        self.assertEqual(
            the_job.holds[0]["releasedBy"], "admin", "Incorrect return type"
        )

    def test_add_hold_returns_error(self):
        # Arrange
        job_id = "abcde12345"
        step_id = "abcde12345"

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).set_current_step(
                step_id=step_id
            )
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Comments

    def test_comments_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = "../README.md"

        # Act
        self.connection.workflow_manager.jobs.get(job_id).add_comment(
            "This is a comment"
        )
        self.connection.workflow_manager.jobs.get(job_id).add_comment(
            "This is a comment"
        )
        comments = self.connection.workflow_manager.jobs.get(job_id).comments
        has_comment = len(comments) == 2

        # Assert
        self.assertIsInstance(comments, list, "Incorrect return type")
        self.assertTrue(has_comment, "comments from job are not returned")

    def test_add_comments_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = "../README.md"

        # Act
        actual = self.connection.workflow_manager.jobs.get(job_id).add_comment(
            "This is a comment"
        )
        comments = self.connection.workflow_manager.jobs.get(job_id).comments
        has_comment = comments[0]["commentId"] == actual

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue(has_comment, "commentId is not added to the job")

    # endregion

    # endregion

    # region Job Template Tests

    # region Get Job Templates

    def test_get_job_templates(self):
        # Act
        job_templates = self.connection.workflow_manager.job_templates

        # Assertions
        self.assertIsInstance(job_templates, list, "Incorrect return type")
        self.assertTrue(len(job_templates) >= 2, "Incorrect number of items downloaded")

    def test_get_valid_job_template(self):
        # Arrange
        valid_template = {
            "description": "A sample workflow introducing some key concepts",
            "job_template_id": "Q5-nYVlCTBOZ4ShEdDsglA",
            "job_template_name": "Introduction to Workflow Manager",
            "state": "Active",
        }

        # Act
        job_templates = self.connection.workflow_manager.job_templates
        found_job_templates = [
            x
            for x in job_templates
            if x.job_template_id == valid_template["job_template_id"]
        ]

        # Assert
        self.assertIsInstance(job_templates, list, "Incorrect return type")
        self.assertTrue(len(job_templates) >= 2, "Incorrect number of items downloaded")
        self.assertTrue(found_job_templates, "Does not contain Default job template")
        self.assertTrue(
            found_job_templates[0].description == valid_template["description"],
            "Default job template is not subscriptable",
        )

    def test_get_job_template(self):
        # Arrange
        default_job_template = {
            "description": "A sample workflow introducing some key concepts",
            "job_template_id": "Q5-nYVlCTBOZ4ShEdDsglA",
            "job_template_name": "Introduction to Workflow Manager",
            "state": "Active",
        }

        # Act
        job_template = self.connection.workflow_manager.job_template(
            "Q5-nYVlCTBOZ4ShEdDsglA"
        )

        # Assert
        self.assertEqual(
            default_job_template["job_template_name"],
            job_template.job_template_name,
            "Incorrect job_template returned",
        )

    def test_get_job_template_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.job_template(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Create Job Templates

    def test_create_job_template_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_job_template()

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")

    # endregion

    # region Update Job Templates

    def test_update_job_template_returns_successfully(self):
        # Arrange
        template_id = self.create_job_template()
        template = self.connection.workflow_manager.job_template(template_id)
        template.description = "Updated Description"
        del template.extended_property_table_definitions

        # Act
        actual = self.connection.workflow_manager.update_job_template(vars(template))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(
            template,
            self.connection.workflow_manager.job_template(template_id),
            "Job template did not update",
        )

    def test_update_job_template_returns_error(self):
        # Arrange

        # Act
        try:
            self.connection.workflow_manager.update_job_template(
                template={
                    "jobTemplateName": "I wanna be done",
                    "category": "ReadyAPI Test Case",
                    "jobTemplate_id": "rdoeTg_8TjGNKB8yg660DA",
                }
            )

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Delete Job Templates

    def test_delete_job_template(self):
        # Arrange
        test_id = self.create_job_template()

        # Act
        delete_job_template = self.connection.workflow_manager.delete_job_template(
            test_id
        )

        # Assert
        self.assertTrue(delete_job_template, "Incorrect return type")

    def test_delete_job_template_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.delete_job_template(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Share Templates

    def test_job_template_share_details_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        search_id = uniqueness[0:22]
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        template_id = self.create_job_template()

        # Act
        template = self.connection.workflow_manager.job_template(template_id)
        actual = template.share_details

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertEqual(actual, [], "Incorrect return type")

        template.share([group["id"]])

        actual_two = template.share_details

        self.assertIsInstance(actual_two, list, "Incorrect return type")
        self.assertEqual(actual_two, [group["id"]], "Incorrect return type")

    def test_share_job_template_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = "Testing Search   " + uniqueness
        search_id = uniqueness[0:22]
        default_group_name = "Workflow Manager Admin " + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group["title"] == default_group_name:
                break

        template_id = self.create_job_template()

        # Act
        template = self.connection.workflow_manager.job_template(template_id)
        actual = template.share([group["id"]])

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertEqual(actual, True, "Incorrect return type")

    # endregion

    # endregion

    # region Diagram Tests

    # region Get Diagrams

    def test_get_valid_diagrams(self):
        # Arrange
        intro_diagram = {
            "active": True,
            "description": "This diagram will provide a walkthrough of some of the basic steps that can "
            "be used to make up a Workflow",
            "diagram_id": "99o2QTePTqq-BHRHK_Aeag",
            "diagramName": "Introduction to Workflow Manager",
        }

        # Act
        diagrams = self.connection.workflow_manager.diagrams
        found_diagrams = [
            x for x in diagrams if x.diagram_id == intro_diagram["diagram_id"]
        ]

        # Assert
        self.assertIsInstance(diagrams, list, "Incorrect return type")
        self.assertGreaterEqual(len(diagrams), 2, "Incorrect number of diagrams")
        self.assertGreater(len(found_diagrams), 0, "Intro diagram was not found")
        self.assertTrue(
            found_diagrams[0].description == intro_diagram["description"],
            "Diagram object is not subscriptable",
        )

    def test_get_specific_diagram(self):
        # Arrange
        test_id = "99o2QTePTqq-BHRHK_Aeag"
        initial_step_id = "df4c8d20-5c99-457f-0be1-21fa8f830760"

        # Act
        diagram = self.connection.workflow_manager.diagram(test_id)

        # Assert
        self.assertEqual(
            "Introduction to Workflow Manager",
            diagram.diagramName,
            "Diagram name did not match",
        )
        self.assertEqual(
            14, len(diagram.steps), "Number of diagram steps did not match"
        )
        self.assertEqual(
            initial_step_id, diagram.initial_step_id, "Initial step Id did not match"
        )
        steps = [x for x in diagram.steps if x["id"] == initial_step_id]
        self.assertGreater(len(steps), 0, "Initial step not found")
        self.assertIsInstance(steps[0], dict, "Incorrect type")

    def test_get_specific_diagram_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.diagram(test_id)

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Get Diagram Version

    def test_get_specific_diagram_version(self):
        # Arrange
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [
                    {"name": "dsource", "sourceType": "string", "url": "string"}
                ],
                "description": "UPDATED",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
            }
        )
        version_one = self.connection.workflow_manager.diagram_version(old_id, 1)
        version_two = self.connection.workflow_manager.diagram_version(old_id, 2)

        # Assert
        self.assertEqual(
            version_one.description, "Test Description", "Incorrect Version description"
        )
        self.assertEqual(
            version_two.description, "UPDATED", "Incorrect Version description"
        )

    def test_get_diagram_version_returns_error(self):
        # Arrange
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [
                    {"name": "dsource", "sourceType": "string", "url": "string"}
                ],
                "description": "UPDATED",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
            }
        )

        # Act
        try:
            # version 3 does not exist
            self.connection.workflow_manager.diagram_version(old_id, 3)

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Get Upgraded Diagram Version

    def test_get_upgraded_diagram_successfully_returns(self):
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.diagram_upgraded_version(old_id, 1)

        self.assertTrue(
            actual["transformedDiagram"],
            "Did not have correct upgraded diagram version",
        )
        self.assertEqual(
            actual["modifiedStepIds"],
            [],
            "Did not have correct upgraded diagram version",
        )
        self.assertEqual(
            actual["failedStepIds"], [], "Did not have correct upgraded diagram version"
        )
        self.assertEqual(
            actual["modifiedDataSourceNames"],
            [],
            "Did not have correct upgraded diagram version",
        )
        self.assertEqual(
            actual["failedDataSourceNames"],
            [],
            "Did not have correct upgraded diagram version",
        )

    # endregion

    # region Delete Diagram Version

    def test_delete_specific_diagram_version(self):
        # Arrange
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [
                    {"name": "dsource", "sourceType": "string", "url": "string"}
                ],
                "description": "UPDATED",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
            }
        )
        version_one = self.connection.workflow_manager.diagram_version(old_id, 1)
        version_two = self.connection.workflow_manager.diagram_version(old_id, 2)

        # Act
        actual = self.connection.workflow_manager.delete_diagram_version(old_id, 2)

        # Assert
        self.assertEqual(
            version_one.description, "Test Description", "Incorrect Version description"
        )
        self.assertEqual(
            version_two.description, "UPDATED", "Incorrect Version description"
        )
        self.assertTrue(actual, "Deleted diagram version successfully")

    def test_delete_diagram_returns_error(self):
        # Arrange
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [
                    {"name": "dsource", "sourceType": "string", "url": "string"}
                ],
                "description": "UPDATED",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
            }
        )

        # Act
        try:
            # version 3 does not exist
            self.connection.workflow_manager.delete_diagram_version(old_id, 3)

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Create Diagrams

    def test_create_diagram_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_diagram()

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(len(actual), 22, "Incorrect size")

    def test_create_diagram_with_cdr_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_diagram_with_cdr()

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(len(actual), 22, "Incorrect size")

    def test_create_diagram_with_Custom_Id_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_diagram_robust()

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(len(actual), 22, "Incorrect size")

    def test_create_diagram_returns_error(self):
        # Arrange

        # Act
        with self.assertRaisesRegex(Exception, "WorkflowDiagram was invalid"):
            # Create a bad diagram
            self.connection.workflow_manager.create_diagram(
                name="Test New Diagram123", display_grid="", steps=None
            )

    # endregion

    # region Update Diagrams

    def test_update_diagram_returns_successfully(self):
        # Arrange

        # Act
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [],
                "description": "UPDATED ",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
            }
        )

        # Assert
        self.assertTrue(actual, "Success was not true")

        # ------------------------------------------------------------------------

    def test_update_diagram_from_upgraded_version_returns_successfully(self):
        # Arrange

        # Act
        old_id = self.create_diagram()
        upgrade_obj = self.connection.workflow_manager.diagram_upgraded_version(
            old_id, 1
        )
        upgrade_obj["transformedDiagram"]["diagramName"] += "UPDATED DIAGRAM"
        upgrade_obj["transformedDiagram"]["active"] = True
        actual = self.connection.workflow_manager.update_diagram(
            body=upgrade_obj["transformedDiagram"], delete_draft=True
        )

        diagram = self.connection.workflow_manager.diagram(old_id)
        # Assert
        self.assertTrue(actual, "Success was not true")

        # ------------------------------------------------------------------------

    def test_update_diagram_with_cdr_returns_successfully(self):
        # Arrange

        # Act
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(
            body={
                "annotations": [],
                "active": True,
                "data_sources": [],
                "description": "UPDATED ",
                "diagram_id": old_id,
                "diagram_name": "UPDATED " + str(datetime.datetime.now()),
                "diagram_version": 2,
                "display_grid": True,
                "initial_step_id": "1640baf9-f934-fd12-2b62-af6bfc2d0e87",
                "initial_step_name": "Start/End",
                "steps": [
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": False,
                        "color": "130, 202, 237",
                        "description": "Step to be put at the start and end of a workflow",
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
                                "nextStep": "21bff5ee-1586-a635-30ea-86769f01ac93",
                                "notifications": [],
                                "points": [{"x": 0, "y": 26}, {"x": 0, "y": 74}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0,0,100,50",
                        "proceedNext": True,
                        "shape": 3,
                        "stepTemplateId": "AVw8d6MdyiKjHtuS9dJ6",
                    },
                    {
                        "action": {"actionType": "Manual"},
                        "automatic": False,
                        "canSkip": True,
                        "color": "242, 226, 121",
                        "description": "Step to indicate manual work, with no additional logic",
                        "helpText": "Manual Step help text",
                        "helpUrl": "Manual Step help url",
                        "id": "21bff5ee-1586-a635-30ea-86769f01ac93",
                        "labelColor": "black",
                        "name": "Manual Step 1",
                        "outlineColor": "242, 226, 121",
                        "paths": [
                            {
                                "assignedType": "Unassigned",
                                "lineColor": "black",
                                "nextStep": "f7c67858-5ccf-f428-9356-72ada9d8600a",
                                "notifications": [],
                                "points": [{"x": 0, "y": 126}, {"x": 0, "y": 174}],
                                "ports": ["BOTTOM", "TOP"],
                            }
                        ],
                        "position": "0, -100, 100, 50",
                        "proceedNext": True,
                        "shape": 1,
                        "stepTemplateId": "AVw8d-MryiKjHtuS9dJ7",
                    },
                ],
                "centralized_data_references": [
                    {
                        "id": "e8e5c963-a485-4f5f-a298-dcf430f72c28",
                        "proItemName": "MyProMapUPDATE",
                        "referenceType": "ProMapItem",
                    }
                ],
                "use_centralized_data_references": True,
            }
        )

        # Assert
        self.assertTrue(actual, "Success was not true")

        # ------------------------------------------------------------------------

    def test_update_diagram_returns_error(self):
        # Arrange

        # Act
        # TODO Create a bad job_template update
        try:
            self.connection.workflow_manager.update_diagram(body={"annotations": []})

        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Delete Diagrams

    def test_delete_diagram(self):
        # Arrange

        # Act
        new_id = self.create_diagram()
        delete_diagram = self.connection.workflow_manager.delete_diagram(new_id)

        # Assert
        self.assertTrue(delete_diagram, "Incorrect return type")

    def test_delete_diagram_returns_job_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.delete_diagram(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Get Job Specific Diagram

    def test_get_job_diagram(self):
        # Act
        # TODO need to be able to load data
        job_id = self.connection.workflow_manager.jobs.create("Q5-nYVlCTBOZ4ShEdDsglA")[
            0
        ]
        job_diagram = self.connection.workflow_manager.jobs.diagram(job_id)

        # Assert
        self.assertEqual(
            "Introduction to Workflow Manager",
            job_diagram.diagram_name,
            "Incorrect diagram name returned",
        )
        self.assertEqual(
            "99o2QTePTqq-BHRHK_Aeag",
            job_diagram.diagram_id,
            "Incorrect diagram id returned",
        )

    def test_get_job_diagram_returns_not_found(self):
        # Arrange
        test_id = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.job_diagram(test_id)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # endregion

    # region Get Table Definitions

    def test_table_definitions_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        template_name = "Testing Template  " + uniqueness
        table_name = "testing_table_" + uniqueness

        # Create Job Template with specific table
        self.create_job_template_robust(
            template_name=template_name, table_name=table_name
        )

        # Act
        actual = self.connection.workflow_manager.table_definitions
        contains_table = False
        for table in actual:
            b = table["tableName"]
            if table["tableName"] == table_name:
                contains_table = True
                break

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertTrue(contains_table, "Incorrect return type")

    # endregion

    # region  LookUp Tables

    # region Get LookUps by Type

    def test_get_lookups(self):
        # Act
        priorities = self.connection.workflow_manager.lookups("priority")
        statuses = self.connection.workflow_manager.lookups("status")

        # Assert
        self.assertIsInstance(statuses.lookups, list, "Incorrect lookups returned")
        self.assertIsInstance(priorities.lookups, list, "Incorrect lookups returned")

    def test_get_lookups_returns_not_found(self):
        # Arrange
        test_type = "bad_id_12345"

        # Act
        try:
            self.connection.workflow_manager.lookups(test_type)
        except Exception as testException:
            assert True, (
                "Expected error returned during test: " + testException.__str__()
            )

    # endregion

    # region Create Look up Table

    def test_create_lookup_successfully_returns(self):
        # Arrange
        lookups = [
            {"lookupName": "Low", "value": 0},
            {"lookupName": "Medium", "value": 5},
            {"lookupName": "High", "value": 10},
            {"lookupName": "EXTRA", "value": 15},
            {"lookupName": "TEST", "value": 110},
        ]

        # Act
        actual = self.connection.workflow_manager.create_lookup("priority", lookups)
        testing = self.connection.workflow_manager.lookups("priority")

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertEqual(actual, True, "Incorrect size")
        self.assertEqual(5, len(testing.lookups), "Incorrect size")

    # endregion

    # region Delete LookupTable

    def test_delete_lookup_successfully_returns(self):
        # Arrange
        lookups = [
            {"lookupName": "Low", "value": 0},
            {"lookupName": "Medium", "value": 5},
            {"lookupName": "High", "value": 10},
            {"lookupName": "EXTRA", "value": 15},
            {"lookupName": "TEST", "value": 110},
        ]

        # Act
        actual = self.connection.workflow_manager.create_lookup("test", lookups)
        testing = self.connection.workflow_manager.delete_lookup("test")

        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertEqual(actual, True, "Incorrect size")
        self.assertIsInstance(testing, bool, "Incorrect return type")
        self.assertEqual(testing, True, "Incorrect size")

    # endregion

    # endregion

    # region Automated Creations

    def test_update_automation_creation_successfully_returns(self):
        # Arrange
        template_id = self.create_job_template()
        adds = [
            {
                "automationName": "test_one",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"NumberOfDays","dayOfMonth":1,"hour":8,"minutes":0}',
            },
            {
                "automationName": "test_two",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"DayOfWeek","dayOfWeek":2,"hour":8,"minutes":0,'
                '"endDate":1921305600000} ',
            },
        ]

        # Act
        template = self.connection.workflow_manager.job_template(template_id)
        actual = template.update_automated_creation(adds)
        creations = template.automated_creations

        # Assert
        self.assertEqual(len(creations), 2, "Incorrect size")

        id_one = creations[0]["automationId"]
        id_two = creations[1]["automationId"]
        adds = [
            {
                "automationName": "test_three",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"NumberOfDays","dayOfMonth":1,"hour":8,"minutes":0}',
            }
        ]
        updates = [{"automationId": id_two, "automationName": "test_two_updated"}]
        deletes = [id_one]

        template.update_automated_creation(adds, updates, deletes)
        creations_two = template.automated_creations

        for c in creations_two:
            if c["automationId"] == id_two:
                break

        self.assertEqual(c["automationName"], "test_two_updated", "Incorrect size")
        self.assertEqual(len(creations_two), 2, "Incorrect size")

    def test_get_automation_creation_successfully_returns(self):
        # Arrange
        template_id = self.create_job_template()
        adds = [
            {
                "automationName": "test_one",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"NumberOfDays","dayOfMonth":1,"hour":8,"minutes":0}',
            },
            {
                "automationName": "test_two",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"DayOfWeek","dayOfWeek":2,"hour":8,"minutes":0,'
                '"endDate":1921305600000} ',
            },
        ]

        # Act
        template = self.connection.workflow_manager.job_template(template_id)
        template.update_automated_creation(adds, [], [])
        creations = template.automated_creations

        # Assert
        self.assertEqual(len(creations), 2, "Incorrect size")

    def test_get_specific_automation_creation_returns_successfully(self):
        # Arrange
        template_id = self.create_job_template()
        adds = [
            {
                "automationName": "test_one",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"NumberOfDays","dayOfMonth":1,"hour":8,"minutes":0}',
            },
            {
                "automationName": "test_two",
                "automationType": "Scheduled",
                "enabled": True,
                "details": '{"timeType":"DayOfWeek","dayOfWeek":2,"hour":8,"minutes":0,'
                '"endDate":1921305600000} ',
            },
        ]

        # Act
        template = self.connection.workflow_manager.job_template(template_id)
        template.update_automated_creation(adds, [], [])
        creations = template.automated_creations

        id_one = creations[0]["automationId"]
        actual = template.automated_creation(id_one)

        # Assert
        self.assertEqual(
            actual["automationName"], "test_one", "Incorrect automated creation found"
        )
        self.assertEqual(
            actual["automationType"], "Scheduled", "Incorrect automated creation found"
        )
        self.assertEqual(len(creations), 2, "Incorrect size")

    # endregion

    # region Templates

    def test_create_template_successfully_returns(self):
        # Arrange
        template = {
            "template_name": "Email Template",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "Look how easy it is to make an email template!",
                "attachmentSelection": "None",
            },
        }

        # Act
        actual = self.connection.workflow_manager.create_template(
            template_type="email",
            template_name="Test Email Template",
            template_details=template["template_details"],
            template_id="Ef42tu_QQMS-IgZc7pOPnQ",
        )
        testing = self.connection.workflow_manager.templates("email")

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(
            actual, {"templateId": "Ef42tu_QQMS-IgZc7pOPnQ"}, "Incorrect size"
        )
        self.assertEqual(1, len(testing), "Incorrect size")

        self.connection.workflow_manager.delete_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )

    def test_update_template_successfully_returns(self):
        # Arrange
        template = {
            "template_name": "Email Template",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "Look how easy it is to make an email template!",
                "attachmentSelection": "None",
            },
        }

        template_two = {
            "template_name": "Email Template 2",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "NEW BODY",
                "attachmentSelection": "None",
            },
        }

        # Act
        self.connection.workflow_manager.create_template(
            template_type="email",
            template_name="Test Email Template",
            template_details=template["template_details"],
            template_id="Ef42tu_QQMS-IgZc7pOPnQ",
        )

        actual = self.connection.workflow_manager.update_template(
            "email",
            "Ef42tu_QQMS-IgZc7pOPnQ",
            "NEW NAME",
            {"body": "NEW EMAIL BODY"},
        )
        testing = self.connection.workflow_manager.get_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )
        # Assert
        self.assertIsInstance(actual, bool, "Incorrect return type")
        self.assertEqual(actual, True, "Incorrect size")
        self.assertEqual(testing.template_name, "NEW NAME", "Incorrect size")
        self.assertEqual(
            "NEW EMAIL BODY" in testing.template_details["body"], True, "Incorrect size"
        )

        self.connection.workflow_manager.delete_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )

    def test_delete_template_successfully_returns(self):
        # Arrange
        template = {
            "template_name": "Email Template",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "Look how easy it is to make an email template!",
                "attachmentSelection": "None",
            },
        }

        self.connection.workflow_manager.create_template(
            template_type="email",
            template_name="Test Email Template",
            template_details=template["template_details"],
            template_id="Ef42tu_QQMS-IgZc7pOPnQ",
        )
        testing = self.connection.workflow_manager.templates("email")
        self.assertEqual(1, len(testing), "Incorrect size")

        # Act
        actual = self.connection.workflow_manager.delete_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )
        testing = self.connection.workflow_manager.templates("email")

        # Assert
        self.assertEqual(actual, True, "Incorrect size")
        self.assertEqual(0, len(testing), "Incorrect size")

    def test_get_templates_successfully_returns(self):
        # Arrange
        template = {
            "template_name": "Email Template",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "Look how easy it is to make an email template!",
                "attachmentSelection": "None",
            },
        }

        # Act
        testing = self.connection.workflow_manager.templates("email")
        self.assertEqual(0, len(testing), "Incorrect size")

        actual = self.connection.workflow_manager.create_template(
            template_type="email",
            template_name="Test Email Template",
            template_details=template["template_details"],
            template_id="Ef42tu_QQMS-IgZc7pOPnQ",
        )
        testing = self.connection.workflow_manager.templates("email")

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(
            actual, {"templateId": "Ef42tu_QQMS-IgZc7pOPnQ"}, "Incorrect size"
        )
        self.assertEqual(1, len(testing), "Incorrect size")

        self.connection.workflow_manager.delete_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )

    def test_get_specific_template_successfully_returns(self):
        # Arrange
        template = {
            "template_name": "Email Template",
            "template_id": "Ef42tu_QQMS-IgZc7pOPnQ",
            "template_details": {
                "to": ["user@esri.com"],
                "cc": ["boss@esri.com"],
                "bcc": ["supervisor@esri.com"],
                "subject": "Workflow Manager Templates",
                "body": "Look how easy it is to make an email template!",
                "attachmentSelection": "None",
            },
        }

        # Act
        template_id = self.connection.workflow_manager.create_template(
            template_type="email",
            template_name="Test Email Template",
            template_details=template["template_details"],
            template_id="Ef42tu_QQMS-IgZc7pOPnQ",
        )
        testing = self.connection.workflow_manager.templates("email")
        actual = self.connection.workflow_manager.get_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )
        # Assert
        self.assertIsInstance(
            actual,
            arcgis.gis.workflowmanager._workflow_manager.Template,
            "Incorrect return type",
        )
        self.assertEqual(actual.template_id, "Ef42tu_QQMS-IgZc7pOPnQ", "Incorrect size")
        self.assertEqual(actual.template_name, "Test Email Template", "Incorrect size")
        self.assertEqual(1, len(testing), "Incorrect size")

        self.connection.workflow_manager.delete_template(
            "email", "Ef42tu_QQMS-IgZc7pOPnQ"
        )

    # endregion

    # region UserType Licenses

    # must be run manually since a user must be added to test properly.
    def test_user_without_UTE_AT_11_2_can_use_workflow_manager(self):
        # Insert credentials for a portal > 11.2
        _conf_reader = ConfigParser()
        credential_path = QALAB_ROOT_PATH + r"\wmx\config.ini"
        _conf_reader.read(credential_path, "UTF-8")

        portal_url = _conf_reader["credentials"]["url_11_2"]
        portal_username = _conf_reader["credentials"]["username"]
        portal_password = _conf_reader["credentials"]["password"]
        workflow_item_id = _conf_reader["credentials"]["workflow_item"]

        gis = GIS(
            url=portal_url,
            username=portal_username,
            password=portal_password,
            verify_cert=False,
        )

        workflow_item = gis.content.get(workflow_item_id)
        workflow_manager = WorkflowManager(workflow_item)

        # Act

        try:
            users = workflow_manager.users

            # Assertions
            self.assertIsInstance(users, list, "Incorrect return type")
            self.assertIsInstance(users[0], dict, "Incorrect type")

        except Exception as testException:
            raise ValueError(
                "User could not use workflow manager api with system. Check UTE and Portal Version"
            )

    # endregion

    # region Step Execution

    def test_run_step_returns_successfully(self):
        # Arrange
        # Create Intro WM Job
        job_id = self.create_job()[0]

        # Act
        job = self.connection.workflow_manager.jobs.get(job_id)
        job_exec = job.run()
        counter = 0

        while not job_exec.done():
            print(f"Status = {job_exec.status}")
            print(f"{job_exec.messages}")
            time.sleep(5)
            counter = counter + 1
            if counter > 10:
                raise TimeoutError('Step did not complete in time')

        # Arrange
        self.assertTrue(job_exec.done(), "Incorrectly  set, execution should be done")
        self.assertEqual(
            MessageType.STEP_INFO_REQUIRED,
            job_exec.result().msg_type,
            "last message should be stepinforequired.",
        )
        self.assertEqual(
            ExecutionStatus.COMPLETE, job_exec.status, "Incorrect return type"
        )
        self.assertTrue(job_exec.messages, "Incorrect return type")

    def test_stop_step_returns_successfully(self):
        # Arrange
        # Create Intro WM Job
        job_id = self.create_job()[0]

        # Act
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.run().result()

        job_exec = job.stop()
        counter = 0

        while not job_exec.done():
            print(f"Status = {job_exec.status}")
            print(f"{job_exec.messages}")
            time.sleep(5)
            counter = counter + 1
            if counter > 10:
                raise TimeoutError('Step did not complete in time')

        # Arrange
        self.assertTrue(job_exec.done(), "Incorrectly  set, execution should be done")
        self.assertEqual(
            MessageType.STEP_PAUSED,
            job_exec.result().msg_type,
            "last message should be stepinforequired.",
        )
        self.assertEqual(
            ExecutionStatus.COMPLETE, job_exec.status, "Incorrect return type"
        )
        self.assertTrue(job_exec.messages, "Incorrect return type")

    def test_finish_step_returns_successfully(self):
        # Arrange
        # Create Intro WM Job
        job_id = self.create_job()[0]

        # Act
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.run().result()
        job.stop().result()
        job_exec = job.finish()
        counter = 0

        while not job_exec.done():
            print(f"Status = {job_exec.status}")
            print(f"{job_exec.messages}")
            time.sleep(5)
            counter = counter + 1
            if counter > 10:
                raise TimeoutError('Step did not complete in time')

        # Arrange
        self.assertTrue(job_exec.done(), "Incorrectly  set, execution should be done")
        self.assertEqual(
            MessageType.STEP_FINISHED,
            job_exec.result().msg_type,
            "last message should be stepinforequired.",
        )
        self.assertEqual(
            ExecutionStatus.COMPLETE, job_exec.status, "Incorrect return type"
        )
        self.assertTrue(job_exec.messages, "Incorrect return type")

    # endregion

    # region Notification Manager
    def test_connect_notification_manager_returns_successfully(self):
        # Arrange
        nm = self.connection.workflow_manager._notification_manager
        nm.connect()

        self.assertTrue(nm.is_connected, "Notification Manager did not connect.")

        nm.disconnect()
        self.assertFalse(nm.is_connected, "Notification Manager did not connect.")

    def test_subscribe_to_job_receives_messages_successfully(self):
        # Arrange
        msgs = []
        nm = self.connection.workflow_manager._notification_manager
        nm.connect()

        self.assertTrue(nm.is_connected, "Notification Manager did not connect.")

        job_id = self.create_job()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)

        def test_callback(notification: Notification, nm: NotificationManager):
            msgs.append(notification)

        nm.subscribe([job_id], test_callback)

        # add a comment get some messages:
        job.add_comment("Hello World")
        self.assertTrue(len(msgs), "Messages were added when subscribed")
        self.assertEqual(
            msgs[0].msg_type,
            MessageType.JOB_COMMENT_UPDATED,
            "Messages were added when subscribed",
        )

        nm.disconnect()
        self.assertFalse(nm.is_connected, "Notification Manager did not connect.")

    def test_unsubscribe_to_job_receives_messages_successfully(self):
        # Arrange
        msgs = []
        nm = self.connection.workflow_manager._notification_manager
        nm.connect()

        self.assertTrue(nm.is_connected, "Notification Manager did not connect.")

        job_id = self.create_job()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)

        def test_callback(notification: Notification, nm: NotificationManager):
            msgs.append(notification)

        nm.subscribe([job_id], test_callback)

        # add a comment get some messages:
        job.add_comment("Hello World")
        self.assertTrue(len(msgs) < 2, "Messages were added when subscribed")
        self.assertEqual(
            msgs[0].msg_type,
            MessageType.JOB_COMMENT_UPDATED,
            "Messages were added when subscribed",
        )

        nm.unsubscribe([job_id])

        job.add_comment("Hello World")
        self.assertTrue(len(msgs) < 2, "Messages were not added when unsubscribed")

        nm.disconnect()
        self.assertFalse(nm.is_connected, "Notification Manager did not connect.")

    # endregion


if __name__ == "__main__":
    unittest.main()
