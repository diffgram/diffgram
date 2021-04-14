from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_new
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

    def test_new_discussion_comment_web(self):
        # Create mock tasks
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)
        comment_content = 'the comment'
        request_data = {
            'content': comment_content
        }

        endpoint = "/api/v1/project/{}/discussion/{}/add-comment".format(self.project.project_string_id, discussion.id)
        auth_api = common_actions.create_project_auth(project = job.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comment' in data)
        self.assertTrue('content' in data['comment'])
        self.assertTrue('user' in data['comment'])
        self.assertTrue(data['comment']['content'] == comment_content)
        self.assertTrue('member_created_id' in data['comment'])
        self.assertTrue('member_updated_id' in data['comment'])
        self.assertTrue('time_created' in data['comment'])
        self.assertTrue('time_updated' in data['comment'])
        self.assertTrue('id' in data['comment'])

    def test_new_discussion_comment_core(self):
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)

        member = self.session.query(Member).filter(
            Member.id == self.project_data['users'][0].member_id
        ).first()
        comment_content = 'the comment.'
        result, log = discussion_comment_new.new_discussion_comment_core(
            session = self.session,
            log = regular_log.default(),
            user = None,
            member = member,
            project = self.project,
            discussion = discussion,
            content = comment_content
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(log['error'].keys()), 0)
