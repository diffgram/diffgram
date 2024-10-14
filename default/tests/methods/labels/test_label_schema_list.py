from methods.regular.regular_api import *  # Import regular API methods
from default.tests.test_utils import testing_setup  # Import testing setup
from shared.tests.test_utils import common_actions, data_mocking  # Import common actions and data mocking utilities
from base64 import b64encode  # Import base64 encoding
from methods.task.task_template.job_list import job_view_core, default_metadata, filter_by_project  # Import job_view_core, default_metadata, and filter_by_project
from unittest.mock import patch  # Import patch for mocking
from methods.task.task_template import job_new_or_update  # Import job_new_or_update
from shared.utils.logging import DiffgramLogger  # Import DiffgramLogger
from shared.database.labels.label_schema import LabelSchema  # Import LabelSchema
from methods.labels.label_schema_list import label_schema_list_core  # Import label_schema_list_core

class TestLabelSchemaList(testing_setup.DiffgramBaseTestCase):
    """
    Test class for testing label schema listing functionality.
    """

    def setUp(self):
        """
        Initializes the project, authentication, and member objects for testing.
        """
        super(TestLabelSchemaList, self).setUp()
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member

    def test_api_label_schema_list(self):
        """
        Tests the API endpoint for label schema listing.
        """
        endpoint = f'/api/v1/project/{self.project.project_string_id}/labels-schema'
        schema1 = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema2 = LabelSchema.new(
            session = self.session,
            name = 'test2',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])

        response = self.client.get(
            endpoint,
            data = json.dumps({}),
            headers = {
                'Authorization': f"Basic {credentials}"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        ids_list = []
        for elm in response.json:
            ids_list.append(elm['id'])

        for id in [schema1.id, schema2.id]:
            self.assertTrue(id in ids_list)

    def test_label_schema_list_core(self):
        """
        Tests the label_schema_list_core function.
        """
        result, log = label_schema_list_core(
            session = self.session,
            project = self.project,
            member = self.member,
            is_default = False
        )
        existing_len = len(result)
        schema1 = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema2 = LabelSchema.new(
            session = self.session,
            name = 'test2',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema3 = LabelSchema.new(
            session = self.session,
            name = 'test2',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema3.archived = True
        self.session.add(schema3)
        self.session.commit()
        result, log = label_schema_list_core(
            session = self.session,
            project = self.project,
            member = self.member,
            is_default = False
        )

        self.assertTrue(len(log['error'].keys()) == 0)
        non_archived_len_expected = 2
        self.assertEqual(len(result), existing_len + non_archived_len_expected)
        for elm in result:
            self.assertTrue(elm['id'] != schema3.id)
