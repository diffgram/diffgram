from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task_template.job_list import job_view_core, default_metadata, filter_by_project
from unittest.mock import patch
from methods.task.task_template import job_new_or_update
from shared.utils.logging import DiffgramLogger
from shared.database.labels.label_schema import LabelSchema
from methods.labels.label_schema_update import label_schema_update_core


class TestLabelSchemaUpdate(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestLabelSchemaUpdate, self).setUp()
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

    def test_api_label_schema_update(self):
        schema1 = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )

        endpoint = f'/api/v1/project/{self.project.project_string_id}/labels-schema/{schema1.id}/update'
        schema_name = 'test_schema'
        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])

        response = self.client.patch(
            endpoint,
            data = json.dumps({'name': schema_name, 'archived': True}),
            headers = {
                'Authorization': f"Basic {credentials}"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], schema_name)
        self.assertEqual(response.json['project_id'], self.project.id)
        self.assertEqual(response.json['archived'], True)
        self.assertEqual(response.json['id'], schema1.id)

    def test_label_schema_list_core(self):
        schema1 = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema_name = 'test_schema'
        result, log = label_schema_update_core(
            session = self.session,
            project = self.project,
            member = self.member,
            schema_id = schema1.id,
            name = schema_name,
            archived = True
        )

        self.assertTrue(len(log['error'].keys()) == 0)
        self.assertEqual(result['name'], schema_name)
        self.assertEqual(result['archived'], schema1.archived)
        self.assertEqual(result['project_id'], self.project.id)
        self.assertIsNotNone(result['id'])
