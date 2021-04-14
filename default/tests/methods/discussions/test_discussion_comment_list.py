from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_list
from unittest.mock import patch
import flask


class TeseIssueNew(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseIssueNew, self).setUp()
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

    def test_list_discussion_comment_web(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)

        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)

        comment2 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)

        request_data = {}
        endpoint = "/api/v1/project/{}/discussion/{}/comments".format(self.project.project_string_id, discussion.id)
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comments' in data)
        self.assertEqual(len(data['comments']), 2)
        ids = [comment['id'] for comment in data['comments']]
        self.assertTrue(comment1.id in ids)
        self.assertTrue(comment2.id in ids)

    def test_list_discussion_comments_core(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)

        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)

        comment2 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)
        result, log = discussion_comment_list.list_discussion_comments_core(
            session = self.session,
            log = regular_log.default(),
            project = self.project,
            discussion = discussion,
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(len(result), 2)
        ids = [x['id'] for x in result]
        self.assertTrue(comment1.id in ids)
        self.assertTrue(comment2.id in ids)
