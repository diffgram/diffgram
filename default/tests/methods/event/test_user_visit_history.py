from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.event import user_visit_history
from unittest.mock import patch
import flask


class TestUserVisitHistory(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestUserVisitHistory, self).setUp()
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

    def test_user_visit_history_api(self):
        # Create mock discussion
        event_1 = data_mocking.create_event({
            'page_name': 'test_page',
            'member_id': self.member.id,
            'kind': 'user_visit',
            'object_type': 'page',
            'project_id': self.project.id,
        }, self.session)

        event_2 = data_mocking.create_event({
            'project_id': self.project.id,
            'page_name': 'test_page2',
            'kind': 'user_visit',
            'member_id': self.member.id,
            'object_type': 'page',
        }, self.session)

        endpoint = f"/api/v1/{self.project.project_string_id}/user-visit-history/"
        credentials = b64encode(f"{self.auth_api.client_id}:{self.auth_api.client_secret}".encode()).decode(
            'utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps({'limit': 50}),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(len(data['user_visit_events']), 2)

        self.assertEqual(data['user_visit_events'][0]['page_name'], event_2.page_name)
        self.assertEqual(data['user_visit_events'][1]['page_name'], event_1.page_name)

    def test_user_visit_history_core(self):
        # Create mock discussion
        event_1 = data_mocking.create_event({
            'page_name': 'test_page',
            'member_id': self.member.id,
            'kind': 'user_visit',
            'object_type': 'page',
            'project_id': self.project.id,
        }, self.session)

        event_2 = data_mocking.create_event({
            'project_id': self.project.id,
            'page_name': 'test_page2',
            'kind': 'user_visit',
            'member_id': self.member.id,
            'object_type': 'page',
        }, self.session)

        event_list = user_visit_history.user_visit_history_core(self.session, self.project, self.member)
        self.assertEqual(len(event_list), 2)
        self.assertEqual(event_list[0]['page_name'], event_2.page_name)
        self.assertEqual(event_list[1]['page_name'], event_1.page_name)
