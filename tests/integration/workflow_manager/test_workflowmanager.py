import unittest
import datetime
from tests.integration.workflow_manager.workflowmanager_setup import WorkflowManagerSetup
import re
from pprint import pprint


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

    def create_diagram(self):
        return self.connection.workflow_manager.create_diagram(
            name='Test New Diagram123 ' + str(datetime.datetime.now().timestamp()),
            display_grid=True,
            description='Test Description',
            active=True,
            annotations=[
                {
                    "position": "0,0,100,250",
                    "color": "130, 202, 237",
                    "outlineColor": "130, 202, 237",
                    "labelColor": "black",
                    "text": "test annotations"
                }
            ],
            data_sources=[
                {
                    "name": "dsource",
                    "url": "string",
                    "sourceType": "string"
                }
            ],
            steps=[{'action': {'actionType': 'Manual'},
                    'automatic': False,
                    'canSkip': False,
                    'color': '130, 202, 237',
                    'description': 'Start and end of a workflow',
                    'helpText': 'Start/End help text',
                    'helpUrl': 'Start/End help url',
                    'id': '1640baf9-f934-fd12-2b62-af6bfc2d0e87',
                    'labelColor': 'black',
                    'name': 'Start/End',
                    'outlineColor': '130, 202, 237',
                    'paths': [{'assignedType': 'Unassigned',
                               'lineColor': 'black',
                               'nextStep': '21bff5ee-1586-a635-30ea'
                                           '-86769f01ac93',
                               'notifications': [],
                               'points': [{'x': 0, 'y': 26},
                                          {'x': 0, 'y': 74}],
                               'ports': ['BOTTOM', 'TOP']}],
                    'position': '0,0,100,50',
                    'proceedNext': True,
                    'shape': 3,
                    'stepTemplateId': 'AVw8d6MdyiKjHtuS9dJ6'}]
        )

    def create_job(self, count=1, template_name='Introduction to Workflow Manager'):
        job_templates = self.connection.workflow_manager.job_templates
        job_template = {}
        for x in job_templates:
            if x.job_template_name == template_name:
                job_template = x

        return self.connection.workflow_manager.jobs.create(template=job_template.job_template_id,
                                                            count=count,
                                                            name='Test New Job123',
                                                            start='2020-04-02T13:25:50Z',
                                                            end='2020-04-02T13:25:50Z',
                                                            priority='High',
                                                            description='hopefully this works...',
                                                            owner=self.connection.portal_username,
                                                            assigned=self.connection.portal_username,
                                                            complete=42,
                                                            notes='testing notes',
                                                            parent=''
                                                            )

    def create_job_template(self):
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))

        name = 'Testing Template  ' + uniqueness
        table_name = 'testing_table_' + uniqueness

        diagrams = self.connection.workflow_manager.diagrams
        diagram = {}
        for gram in diagrams:
            if gram.diagram_name == 'Introduction to Workflow Manager':
                diagram = gram
                break

        return self.connection.workflow_manager.create_job_template(name=name,
                                                                    diagram_id=diagram.diagram_id,
                                                                    diagram_name=diagram.diagram_name,
                                                                    priority='high',
                                                                    category='Functional Tests',
                                                                    job_duration=5,
                                                                    assigned_to=self.connection.portal_username,
                                                                    default_due_date='2020-04-02T13:25:50Z',
                                                                    default_start_date='2020-04-02T13:25:50Z',
                                                                    start_date_type='CreationDate',
                                                                    assigned_type='Unassigned',
                                                                    description='Test Test test',
                                                                    default_description='Test Test123',
                                                                    state='Active',
                                                                    last_updated_by='Abbie Admin',
                                                                    last_updated_date='2020-04-02T13:25:50Z',
                                                                    extended_property_table_definitions=[
                                                                        {
                                                                            "tableName": table_name,
                                                                            "tableAlias": table_name,
                                                                            "tableOrder": 0,
                                                                            "relationshipType": "OneToOne",
                                                                            "extendedPropertyDefinitions": [
                                                                                {"propertyOrder": 0,
                                                                                 "visible": True,
                                                                                 "propertyName": "string",
                                                                                 "editable": True,
                                                                                 "domain": {
                                                                                     "type": "codedValue",
                                                                                     "codedValues": [
                                                                                         {
                                                                                             "code": "string",
                                                                                             "name": "string"
                                                                                         }
                                                                                     ],
                                                                                     "range": [
                                                                                         "string"
                                                                                     ]
                                                                                 },
                                                                                 "dataType": "String",
                                                                                 "propertyAlias": "string",
                                                                                 "required": True,
                                                                                 "fieldLength": 0
                                                                                 }
                                                                            ],
                                                                        }
                                                                    ]
                                                                    )

    # endregion

    # region Users

    def test_get_assignable_users(self):
        # Act
        assignable_users = self.connection.workflow_manager.assignable_users

        # Assertions
        self.assertIsInstance(assignable_users, list, "Incorrect return type")
        self.assertEqual(len(assignable_users), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(assignable_users[0], dict, "Incorrect type")

    def test_get_valid_assignable_users(self):
        # Arrange
        valid_assignable_user = {'email': 'admin@mydomain.com', 'fullName': 'Administrator', 'username': 'admin'}

        # Act
        assignable_users = self.connection.workflow_manager.assignable_users

        # Assert
        self.assertIsInstance(assignable_users, list, "Incorrect return type")
        self.assertEqual(len(assignable_users), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(assignable_users[0], dict, "Incorrect type")

    def test_get_users(self):
        # Act
        users = self.connection.workflow_manager.users

        # Assertions
        self.assertIsInstance(users, list, "Incorrect return type")
        self.assertEqual(len(users), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(users[0], dict, "Incorrect type")

    def test_get_valid_users(self):
        # Arrange
        valid_user = {'email': 'admin@mydomain.com', 'fullName': 'Administrator', 'username': 'admin'}

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
            if user['username'] == self.connection.portal_username:
                default_user = user
                break

        # Act
        user = self.connection.workflow_manager.user(default_user['username'])

        # Assert
        self.assertEqual(default_user['username'], user.username, "Incorrect role returned")

    def test_get_specific_user_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.role(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        valid_role = {'description': 'Role with basic privileges to manage jobs. Privileges '
                                     'assigned are assign job to group, assign job to individual, '
                                     'update holds, attachments and queries',
                      'privileges': ['jobAssignGroup',
                                     'jobUpdateHolds',
                                     'jobUpdateAttachments',
                                     'queryUpdate',
                                     'jobAssignIndividual',
                                     'viewWorkPage',
                                     'viewCreatePanel',
                                     'viewDetailsPanelAttachments',
                                     'viewDetailsPanelProperties',
                                     'viewDetailsPanelLocation'],
                      'role_name': 'Manage Jobs - Basic'}

        # Act
        roles = self.connection.workflow_manager.wm_roles
        found_role = [x for x in roles if x.role_name == valid_role['role_name']]

        # Assert
        self.assertIsInstance(roles, list, "Incorrect return type")
        self.assertEqual(len(roles), 5, "Incorrect number of items downloaded")
        self.assertTrue(found_role, 'Does not contain default role')

    def test_get_specific_wm_role(self):
        # Arrange
        test_name = 'Manage Jobs - Basic'

        # Act
        role = self.connection.workflow_manager.wm_role(test_name)

        # Assert
        self.assertEqual('Manage Jobs - Basic', role.role_name, "Incorrect role returned")

    def test_get_specific_wm_role_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.wm_role(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    def test_create_wm_role_successfully_returns(self):
        # Arrange

        # Act
        actual = self.connection.workflow_manager.create_wm_role(name='Test New Role',
                                                                 description='Test Description',
                                                                 privileges=['adminAdvanced', 'jobCreate', 'jobDelete']
                                                                 )

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_create_wm_role_returns_error(self):
        # Arrange

        # Act
        try:
            self.connection.workflow_manager.create_wm_role(name='Test New Role',
                                                            description='Test Description',
                                                            privileges=['fakePrivilege123', 'jobCreate', 'jobDelete']
                                                            )
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Groups

    def test_get_assignable_groups(self):
        # Act
        assignable_groups = self.connection.workflow_manager.assignable_groups

        # Assertions
        self.assertIsInstance(assignable_groups, list, "Incorrect return type")
        self.assertEqual(len(assignable_groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(assignable_groups[0], dict, "Incorrect type")

    def test_get_valid_assignable_groups(self):
        # Arrange
        default_group_name = 'Workflow Manager Admin ' + self.connection.item_name

        # Act
        groups = self.connection.workflow_manager.assignable_groups
        found_group = [x for x in groups if x['title'] == default_group_name]

        # Assert
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")
        self.assertTrue(found_group, 'Does not contain default group')

    def test_get_groups(self):
        # Act
        groups = self.connection.workflow_manager.assignable_groups

        # Assertions
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")

    def test_get_valid_groups(self):
        # Arrange
        default_group_name = 'Workflow Manager Admin ' + self.connection.item_name

        # Act
        groups = self.connection.workflow_manager.groups
        found_group = [x for x in groups if x['title'] == default_group_name]

        # Assert
        self.assertIsInstance(groups, list, "Incorrect return type")
        self.assertEqual(len(groups), 1, "Incorrect number of items downloaded")
        self.assertIsInstance(groups[0], dict, "Incorrect type")
        self.assertTrue(found_group, 'Does not contain default group')

    def test_get_specific_group(self):
        # Arrange
        default_group_name = 'Workflow Manager Admin ' + self.connection.item_name
        groups = self.connection.workflow_manager.groups

        for group in groups:
            if group['title'] == default_group_name:
                break

        # Act
        # returns object with roles assigned to group
        specific_group = self.connection.workflow_manager.group(group['id'])
        has_group = 'Workflow Administrator' in specific_group.roles

        # Assert
        self.assertTrue(has_group, "Incorrect group with included roles returned")

    def test_get_specific_group_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.group(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Searches

    def test_get_searches(self):
        # Act
        searches = self.connection.workflow_manager.searches

        # Assertions
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertEqual(len(searches), 3, "Incorrect number of items downloaded")
        self.assertIsInstance(searches[0], dict, "Incorrect type")

    def test_get_valid_searches(self):
        # Arrange
        valid_search = {'definition': {'displayNames': ['Assigned To',
                                                        'Name',
                                                        'Current Step',
                                                        'Type',
                                                        'Priority',
                                                        'Due Date',
                                                        'Status'],
                                       'fields': ['assignedTo',
                                                  'jobName',
                                                  'currentStep',
                                                  'jobTemplateName',
                                                  'priority',
                                                  'dueDate',
                                                  'jobStatus'],
                                       'num': 50,
                                       'q': '"assignedType=\'User\' AND closed=0 AND assignedTo=\'" '
                                            '+ $currentUser + "\' "',
                                       'sortFields': [{'field': 'jobName', 'sortOrder': 'Asc'},
                                                      {'field': 'priority', 'sortOrder': 'Asc'}],
                                       'start': 0},
                        'name': 'My Jobs',
                        'searchId': 'rrUF60TFQCe2K0vtgSsYpA',
                        'searchType': 'Standard',
                        'sortIndex': 1000}

        # Act
        searches = self.connection.workflow_manager.searches
        has_search = valid_search in searches

        # Assert
        self.assertIsInstance(searches, list, "Incorrect return type")
        self.assertEqual(len(searches), 3, "Incorrect number of items downloaded")
        self.assertIsInstance(searches[0], dict, "Incorrect type")
        self.assertTrue(has_search, 'Does not contain default search')

    def test_search_jobs_successfully_returns_with_default_fields(self):
        # Arrange
        diagram_id = 'abcde12345'
        user_query = "assignedType='User' AND closed=0 AND diagramId='" + diagram_id + "' "
        expected = {'q': "assigned_type='User' AND closed=0 AND diagram='abcde12345' ",
                    'fields': [{'name': 'jobName', 'fieldType': 'String'},
                               {'name': 'priority', 'fieldType': 'String'},
                               {'name': 'dueDate', 'fieldType': 'DateTime'},
                               {'name': 'currentStep', 'fieldType': 'String'}],
                    'results': [],
                    'start': 0,
                    'next_start': -1,
                    'num': 0}

        expected_job_list = []

        # Act
        # No fields selected so expect default fields of jobName, priority, dueDate and currentStep
        actual = self.connection.workflow_manager.jobs.search(query=user_query)
        job_list = actual.get('results')

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(actual, expected, "Incorrect search returned")
        self.assertEqual(job_list, expected_job_list, "Incorrect search returned")

    def test_search_jobs_successfully_returns_with_selected_fields(self):
        # Arrange
        diagram_id = 'abcde12345'
        user_query = "assignedType='User' AND closed=0 AND diagramId='" + diagram_id + "' "
        expected = {'q': "assigned_type='User' AND closed=0 AND diagram='abcde12345' ",
                    'fields': [{'name': 'jobId', 'fieldType': 'String'},
                               {'name': 'diagramVersion', 'fieldType': 'Integer'}],
                    'results': [],
                    'start': 0,
                    'next_start': -1,
                    'num': 0}

        expected_job_list = []

        # Act
        actual = self.connection.workflow_manager.jobs.search(query=user_query, fields=['jobId', 'diagramVersion'])
        job_list = actual.get('results')

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertEqual(actual, expected, "Incorrect search returned")
        self.assertEqual(job_list, expected_job_list, "Incorrect search returned")

    def test_search_jobs_returns_error(self):
        # Arrange
        diagram_id = 'abcde12345'
        user_query = "assignedType='User' AND closed=0 AND diagram_id='" + diagram_id + "' "

        # Act
        try:
            self.connection.workflow_manager.search_jobs(query=user_query, fields=['jobId', 'diagramVersion'])
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Settings

    def test_get_valid_settings(self):
        # Arrange
        valid_settings = [{"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name"},
                          {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
                          {"propName": "smtpUsername", "value": "new_admin"},
                          {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
                          {"propName": "smtpPort", "value": "3113"},
                          {"propName": "smtpProtocol", "value": "New Protocol"},
                          {"propName": "smtpServer", "value": "New Server"}
                          ]

        # Add settings
        self.connection.workflow_manager.update_settings(valid_settings)

        # Act
        settings = self.connection.workflow_manager.settings
        has_setting = [x for x in settings if
                       x['propName'] == 'smtpDefaultSenderDisplayName' and x['value'] == 'Updated Name']

        # Assert
        self.assertIsInstance(settings, list, "Incorrect return type")
        self.assertTrue(has_setting, 'Does not contain default settings')

    def test_update_settings_returns_successfully(self):
        # Arrange
        uniqueness = re.sub("[^0-9a-z]+", "_", str(datetime.datetime.now()))
        settings = [{"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name" + uniqueness},
                    {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
                    {"propName": "smtpUsername", "value": "new_admin"},
                    {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
                    {"propName": "smtpPort", "value": "3113"},
                    {"propName": "smtpProtocol", "value": "New Protocol"},
                    {"propName": "smtpServer", "value": "New Server"}
                    ]

        updated_settings = [{"propName": "smtpDefaultSenderDisplayName", "value": "Updated Name"},
                            {"propName": "smtpDefaultSenderEmail", "value": "update@wmx.com"},
                            {"propName": "smtpUsername", "value": "new_admin"},
                            {"propName": "smtpPassword", "value": "n3W_p@$sw0Rd"},
                            {"propName": "smtpPort", "value": "3113"},
                            {"propName": "smtpProtocol", "value": "New Protocol"},
                            {"propName": "smtpServer", "value": "New Server"}
                            ]

        # Act
        actual = self.connection.workflow_manager.update_settings(props=updated_settings)

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(settings, self.connection.workflow_manager.settings,
                            "Incorrect updated settings is returned")

    def test_update_settings_returns_error(self):
        # Arrange
        updated_settings = [{'propName': 'string', 'value': 'string'}, {'propName2': 'string', 'value': 'string'}]

        # Act
        # TODO Create a bad settings update
        try:
            self.connection.workflow_manager.update_settings(props=updated_settings)

        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Evaluate Arcade

    def test_evaluate_arcade_job_context(self):
        # Arrange
        expression1 = "'Job name = ' + jobName($job)"

        # Act
        # TODO Need to be able to load test data
        expected_name = 'Arcade @ Tests'
        job_id = self.connection.workflow_manager.jobs.create('Q5-nYVlCTBOZ4ShEdDsglA', name=expected_name)[0]
        result1 = self.connection.workflow_manager.evaluate_arcade(expression1, context_type="JobContext",
                                                                   context={'jobId': job_id})
        result2 = self.connection.workflow_manager.evaluate_arcade(expression1, context_type="JobContext",
                                                                   context={'jobId': job_id}, mode='URL')

        # Assert
        self.assertEqual(f'Job name = {expected_name}', result1, 'Arcade results with job context did not match')
        self.assertEqual(f'Job name = Arcade+%40+Tests', result2, 'Arcade results with URL mode did not match')

    def test_evaluate_arcade_base_context(self):
        # Arrange
        expression1 = "'test ' + '123'"

        # Act
        result1 = self.connection.workflow_manager.evaluate_arcade(expression1)

        # Assert
        self.assertEqual('test 123', result1, 'Arcade results did not match')

    def test_evaluate_arcade_returns_error(self):
        # Act
        expression1 = "'test '"

        try:
            # TODO add bad expression
            self.connection.workflow_manager.evaluate_arcade(expression1, context={'jobId': 'abc123'})
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.jobs.get(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Create Jobs

    def test_create_job_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_job()

        # Assert
        self.assertIsInstance(actual, list, "Incorrect return type")
        self.assertIsInstance(actual[0], str, "Incorrect return type")

    def test_create_multiple_job_successfully_returns(self):
        # Arrange
        job_templates = self.connection.workflow_manager.job_templates
        job_template = {}
        for x in job_templates:
            if x.job_template_name == 'Introduction to Workflow Manager':
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
            self.create_job(template_name='Route Edits')

        except Exception as testException:
            self.assertTrue('Route Edits is not active' in str(testException), 'Incorrect Exception returned')

    # endregion Create Jobs

    # region Update Jobs

    def test_update_job_successfully_returns(self):
        # Arrange
        job_id = self.create_job()[0]
        job = self.connection.workflow_manager.jobs.get(job_id)
        job.priority = 'Updated'

        # Act
        actual = self.connection.workflow_manager.jobs.update(job_id, vars(job))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(job, self.connection.workflow_manager.jobs.get(job_id), "Job did not update")

    def test_update_job_returns_error(self):
        # Arrange
        job_id = 'abcde12345'

        updated_job_object = {"job_id": job_id, "jobName": "Standard"}

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).update(updated_job_object)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        test_id = ['bad_id_12345']

        # Act
        try:
            self.connection.workflow_manager.jobs.close(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.jobs.upgrade(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Job Location

    # TODO Re-implement Job Location Gets all location types

    def test_get_job_location_returns_no_location_set(self):
        # Arrange
        test_id = self.create_job()[0]

        default_job_location = {'geometry': '{}',
                                'geometryType': 'None'}

        # Act
        job_location = self.connection.workflow_manager.jobs.get(test_id).location

        # Assert
        self.assertEqual(default_job_location['geometryType'], str(job_location.geometryType),
                         "Incorrect job location returned")

    # endregion

    # region Job Attachments

    def test_job_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = '../README.md'

        # Act
        attachment = self.connection.workflow_manager.jobs.get(job_id).add_attachment(url)
        actual = self.connection.workflow_manager.jobs.get(job_id).get_attachment(attachment['id'])

        # Arrange
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertTrue('README.md' in actual, 'Did not return correct attachment')

    def test_job_attachment_returns_error(self):
        # Arrange
        job_id = 'abcde12345'
        attachment_id = 'abcde12345'

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).get_attachment(attachment_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    def test_add_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = '../README.md'

        # Act
        actual = self.connection.workflow_manager.jobs.get(job_id).add_attachment(url)
        has_attachment = self.connection.workflow_manager.jobs.get(job_id).get_attachment(actual['id'])

        # Assert
        self.assertIsInstance(actual, dict, "Incorrect return type")
        self.assertTrue(has_attachment, "Attachment is not is returned from job")

    def test_add_attachment_returns_error_bad_url(self):
        # Arrange
        job_id = self.create_job()[0]

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).add_attachment('bad_id')
        except Exception as testException:
            print(testException)
            assert True, "Expected error returned during test: " + testException.__str__()

    def test_update_attachment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        url = '../README.md'
        attachment = self.connection.workflow_manager.jobs.get(job_id).add_attachment(url)
        attachment_id = attachment['id']
        alias = 'Updated alias'

        # Act
        actual = self.connection.workflow_manager.jobs.get(job_id).update_attachment(attachment_id, alias)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")

    def test_delete_job_attachment(self):
        # Arrange
        test_id = self.create_job()[0]
        url = '../README.md'
        attachment_id = self.connection.workflow_manager.jobs.get(test_id).add_attachment(url)['id']

        # Act
        actual = self.connection.workflow_manager.jobs.delete_attachment(test_id, attachment_id)

        # Assert
        self.assertTrue(actual, "Incorrect return type")

    def test_delete_attachment_returns_not_found(self):
        # Arrange
        test_id = self.create_job()[0]
        url = '../README.md'
        attachment_id = self.connection.workflow_manager.jobs.get(test_id).add_attachment(url)['id']

        # Act
        actual = self.connection.workflow_manager.jobs.delete_attachment(test_id, attachment_id)

        # Try deleting non-existing attachment
        try:
            self.connection.workflow_manager.jobs.delete_attachment(test_id, attachment_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        job_id = 'abcde12345'

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).history
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Update Step Assignment

    def test_update_step_assignment_returns_successfully(self):
        # Arrange
        job_id = self.create_job()[0]
        diagram = self.connection.workflow_manager.jobs.diagram(job_id)
        step_id = diagram.initial_step_id

        actual = self.connection.workflow_manager.jobs.get(job_id).update_step(step_id=step_id,
                                                                               assigned_type='User',
                                                                               assigned_to=self.connection.portal_username)

        # Arrange
        self.assertTrue(actual, "Incorrect return type")

    def test_update_step_assignment_returns_error(self):
        # Arrange
        job_id = 'abcde12345'
        step_id = 'abcde12345'
        assignment_type = 'Group'

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).update_step(step_id=step_id,
                                                                          assigned_type=assignment_type,
                                                                          assigned_to='Unknown')
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        job_id = 'abcde12345'
        step_id = 'abcde12345'

        # Act
        try:
            self.connection.workflow_manager.jobs.get(job_id).set_current_step(step_id=step_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        valid_template = {'description': 'A sample workflow introducing some key concepts',
                          'job_template_id': 'Q5-nYVlCTBOZ4ShEdDsglA',
                          'job_template_name': 'Introduction to Workflow Manager',
                          'state': 'Active'}

        # Act
        job_templates = self.connection.workflow_manager.job_templates
        found_job_templates = [x for x in job_templates if x.job_template_id == valid_template['job_template_id']]

        # Assert
        self.assertIsInstance(job_templates, list, "Incorrect return type")
        self.assertTrue(len(job_templates) >= 2, "Incorrect number of items downloaded")
        self.assertTrue(found_job_templates, 'Does not contain Default job template')
        self.assertTrue(found_job_templates[0].description == valid_template['description'],
                        'Default job template is not subscriptable')

    def test_get_job_template(self):
        # Arrange
        default_job_template = {'description': 'A sample workflow introducing some key concepts',
                                'job_template_id': 'Q5-nYVlCTBOZ4ShEdDsglA',
                                'job_template_name': 'Introduction to Workflow Manager',
                                'state': 'Active'}

        # Act
        job_template = self.connection.workflow_manager.job_template('Q5-nYVlCTBOZ4ShEdDsglA')

        # Assert
        self.assertEqual(default_job_template['job_template_name'], job_template.job_template_name,
                         "Incorrect job_template returned")

    def test_get_job_template_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.job_template(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        template.description = 'Updated Description'
        del template.extended_property_table_definitions

        # Act
        actual = self.connection.workflow_manager.update_job_template(vars(template))

        # Assert
        self.assertTrue(actual, "Incorrect return type")
        self.assertNotEqual(template, self.connection.workflow_manager.job_template(template_id),
                            "Job template did not update")

    def test_update_job_template_returns_error(self):
        # Arrange

        # Act
        try:
            self.connection.workflow_manager.update_job_template(
                template={
                    'jobTemplateName': 'I wanna be done',
                    'category': 'ReadyAPI Test Case',
                    'jobTemplate_id': 'rdoeTg_8TjGNKB8yg660DA',
                }
            )

        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Delete Job Templates

    def test_delete_job_template(self):
        # Arrange
        test_id = self.create_job_template()

        # Act
        delete_job_template = self.connection.workflow_manager.delete_job_template(test_id)

        # Assert
        self.assertTrue(delete_job_template, "Incorrect return type")

    def test_delete_job_template_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.delete_job_template(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # endregion

    # region Diagram Tests

    # region Get Diagrams

    def test_get_valid_diagrams(self):
        # Arrange
        intro_diagram = {'active': True,
                         'description': 'This diagram will provide a walkthrough of some of the basic steps that can '
                                        'be used to make up a Workflow',
                         'diagram_id': '99o2QTePTqq-BHRHK_Aeag',
                         'diagramName': 'Introduction to Workflow Manager'}

        # Act
        diagrams = self.connection.workflow_manager.diagrams
        found_diagrams = [x for x in diagrams if x.diagram_id == intro_diagram['diagram_id']]

        # Assert
        self.assertIsInstance(diagrams, list, "Incorrect return type")
        self.assertGreaterEqual(len(diagrams), 2, "Incorrect number of diagrams")
        self.assertGreater(len(found_diagrams), 0, "Intro diagram was not found")
        self.assertTrue(found_diagrams[0].description == intro_diagram['description'],
                        "Diagram object is not subscriptable")

    def test_get_specific_diagram(self):
        # Arrange
        test_id = '99o2QTePTqq-BHRHK_Aeag'
        initial_step_id = 'df4c8d20-5c99-457f-0be1-21fa8f830760'

        # Act
        diagram = self.connection.workflow_manager.diagram(test_id)

        # Assert
        self.assertEqual("Introduction to Workflow Manager", diagram.diagramName, 'Diagram name did not match')
        self.assertEqual(14, len(diagram.steps), 'Number of diagram steps did not match')
        self.assertEqual(initial_step_id, diagram.initial_step_id, 'Initial step Id did not match')
        steps = [x for x in diagram.steps if x['id'] == initial_step_id]
        self.assertGreater(len(steps), 0, 'Initial step not found')
        self.assertIsInstance(steps[0], dict, "Incorrect type")

    def test_get_specific_diagram_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        with self.assertRaisesRegex(Exception, 'Diagram bad_id_12345 was not found'):
            self.connection.workflow_manager.diagram(test_id)

    # endregion

    # region Create Diagrams

    def test_create_diagram_successfully_returns(self):
        # Arrange

        # Act
        actual = self.create_diagram()

        # Assert
        self.assertIsInstance(actual, str, "Incorrect return type")
        self.assertEqual(len(actual), 22, "Incorrect size")

    def test_create_diagram_returns_error(self):
        # Arrange

        # Act
        with self.assertRaisesRegex(Exception, 'WorkflowDiagram was invalid'):
            # Create a bad diagram
            self.connection.workflow_manager.create_diagram(name='Test New Diagram123', display_grid='', steps=None)

    # endregion

    # region Update Diagrams

    def test_update_diagram_returns_successfully(self):
        # Arrange

        # Act
        old_id = self.create_diagram()
        actual = self.connection.workflow_manager.update_diagram(body={'annotations': [],
                                                                       'active': True,
                                                                       'data_sources': [
                                                                           {'name': 'dsource', 'sourceType': 'string',
                                                                            'url': 'string'}],
                                                                       'description': 'UPDATED ',
                                                                       'diagram_id': old_id,
                                                                       'diagram_name': 'UPDATED ' + str(
                                                                           datetime.datetime.now()),
                                                                       'diagram_version': 2,
                                                                       'display_grid': True,
                                                                       'initial_step_id': '1640baf9-f934-fd12-2b62-af6bfc2d0e87',
                                                                       'initial_step_name': 'Start/End',
                                                                       'steps': [{'action': {'actionType': 'Manual'},
                                                                                  'automatic': False,
                                                                                  'canSkip': False,
                                                                                  'color': '130, 202, 237',
                                                                                  'description': 'Step to be put at the start and end of a workflow',
                                                                                  'helpText': 'Start/End help text',
                                                                                  'helpUrl': 'Start/End help url',
                                                                                  'id': '1640baf9-f934-fd12-2b62-af6bfc2d0e87',
                                                                                  'labelColor': 'black',
                                                                                  'name': 'Start/End',
                                                                                  'outlineColor': '130, 202, 237',
                                                                                  'paths': [
                                                                                      {'assignedType': 'Unassigned',
                                                                                       'lineColor': 'black',
                                                                                       'nextStep': '21bff5ee-1586-a635-30ea-86769f01ac93',
                                                                                       'notifications': [],
                                                                                       'points': [{'x': 0, 'y': 26},
                                                                                                  {'x': 0, 'y': 74}],
                                                                                       'ports': ['BOTTOM', 'TOP']}],
                                                                                  'position': '0,0,100,50',
                                                                                  'proceedNext': True,
                                                                                  'shape': 3,
                                                                                  'stepTemplateId': 'AVw8d6MdyiKjHtuS9dJ6'},
                                                                                 {'action': {'actionType': 'Manual'},
                                                                                  'automatic': False,
                                                                                  'canSkip': True,
                                                                                  'color': '242, 226, 121',
                                                                                  'description': 'Step to indicate manual work, with no additional logic',
                                                                                  'helpText': 'Manual Step help text',
                                                                                  'helpUrl': 'Manual Step help url',
                                                                                  'id': '21bff5ee-1586-a635-30ea-86769f01ac93',
                                                                                  'labelColor': 'black',
                                                                                  'name': 'Manual Step 1',
                                                                                  'outlineColor': '242, 226, 121',
                                                                                  'paths': [
                                                                                      {'assignedType': 'Unassigned',
                                                                                       'lineColor': 'black',
                                                                                       'nextStep': 'f7c67858-5ccf-f428-9356-72ada9d8600a',
                                                                                       'notifications': [],
                                                                                       'points': [{'x': 0, 'y': 126},
                                                                                                  {'x': 0, 'y': 174}],
                                                                                       'ports': ['BOTTOM', 'TOP']}],
                                                                                  'position': '0, -100, 100, 50',
                                                                                  'proceedNext': True,
                                                                                  'shape': 1,
                                                                                  'stepTemplateId': 'AVw8d-MryiKjHtuS9dJ7'}]
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
            self.connection.workflow_manager.update_diagram(body={'annotations': []})

        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

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
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.delete_diagram(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # region Get Job Specific Diagram

    def test_get_job_diagram(self):
        # Act
        # TODO need to be able to load data
        job_id = self.connection.workflow_manager.jobs.create('Q5-nYVlCTBOZ4ShEdDsglA')[0]
        job_diagram = self.connection.workflow_manager.jobs.diagram(job_id)

        # Assert
        self.assertEqual('Introduction to Workflow Manager', job_diagram.diagram_name,
                         "Incorrect diagram name returned")
        self.assertEqual('99o2QTePTqq-BHRHK_Aeag', job_diagram.diagram_id, "Incorrect diagram id returned")

    def test_get_job_diagram_returns_not_found(self):
        # Arrange
        test_id = 'bad_id_12345'

        # Act
        try:
            self.connection.workflow_manager.job_diagram(test_id)
        except Exception as testException:
            assert True, "Expected error returned during test: " + testException.__str__()

    # endregion

    # endregion


if __name__ == "__main__":
    unittest.main()
