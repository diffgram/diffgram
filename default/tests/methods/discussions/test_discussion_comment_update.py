from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_update
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

    def test_update_discussion_comment_web(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        member = auth_api.member
        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'member_created_id': member.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)

        new_content = 'new content.'
        request_data = {
            'comment_id': comment1.id,
            'content': new_content
        }
        endpoint = "/api/v1/project/{}/discussion/{}/update-comment".format(self.project.project_string_id, discussion.id)

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
        self.assertTrue('comment' in data)
        self.assertEqual(data['comment']['content'], new_content)

    def test_update_discussion_comments_core(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)

        member = self.project_data['users'][0].member

        comment1 = data_mocking.create_discussion_comment({
            'discussion_id': discussion.id,
            'member_created_id': member.id,
            'project_id': self.project.id,
            'content': 'test'
        }, self.session)

        new_content = 'new content.'
        result, log = discussion_comment_update.update_discussion_comments_core(
            session = self.session,
            comment_id = comment1.id,
            content = new_content,
            member = member,
            log = regular_log.default(),
        )
        self.assertTrue(len(log['error'].keys()) == 0)
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], new_content)
