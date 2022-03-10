from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.event import event_create
from unittest.mock import patch
import flask


class TestEventCreate(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestEventCreate, self).setUp()
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
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member

    def test_api_event_create(self):
        # Create mock discussion
        request_data = {
            'page_name': 'test_page2',
            'kind': 'user_visit',
            'member_id': self.member.id,
            'object_type': 'page',
        }

        endpoint = f"/api/v1/project/{self.project.project_string_id}/event/create"
        credentials = b64encode(f"{self.auth_api.client_id}:{self.auth_api.client_secret}".encode()).decode(
            'utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(data['created_event']['page_name'], request_data['page_name'])
        self.assertEqual(data['created_event']['kind'], request_data['kind'])
        self.assertEqual(data['created_event']['member_id'], request_data['member_id'])
        self.assertEqual(data['created_event']['object_type'], request_data['object_type'])
        self.assertIsNotNone(data['created_event']['id'])

    def test_event_create_core(self):
        # Create mock discussion
        request_data = {
            'page_name': 'test_page2',
            'kind': 'user_visit',
            'member_id': self.member.id,
            'object_type': 'page',
        }

        event_data = event_create.event_create_core(self.session, None,
                                                    self.member,
                                                    self.project,
                                                    request_data['object_type'], request_data['kind'],
                                                    request_data['page_name'])
        self.assertEqual(event_data['page_name'], request_data['page_name'])
        self.assertEqual(event_data['kind'], request_data['kind'])
        self.assertEqual(event_data['member_id'], request_data['member_id'])
        self.assertEqual(event_data['object_type'], request_data['object_type'])
        self.assertIsNotNone(event_data['id'])
