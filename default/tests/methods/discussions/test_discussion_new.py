from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.discussions import discussion_new
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

    def test_issue_new_web(self):
        # Create mock tasks
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        task = data_mocking.create_task({
            'name': 'task{}'.format(1),
            'job': job,
            'file': file,
        }, self.session)
        discussion_title = 'new_issue'
        discussion_description = 'new_issue_description'
        request_data = {
            'title': discussion_title,
            'description': discussion_description,
            'attached_elements': [
                {'type': 'job', 'id': job.id},
                {'type': 'file', 'id': file.id},
                {'type': 'task', 'id': task.id}
            ]
        }

        endpoint = "/api/v1/project/" + job.project.project_string_id + "/issues/new"
        auth_api = common_actions.create_project_auth(project=job.project, session=self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(job.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['issue']['title'], discussion_title)
        self.assertEqual(data['issue']['description'], discussion_description)

    def test_new_issue_core(self):
        # Create mock tasks
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job'
        }, self.session)

        file = data_mocking.create_file({'project_id': job.project.id, 'job_id': job.id}, self.session)
        task = data_mocking.create_task({
            'name': 'task{}'.format(1),
            'job': job,
            'file': file,
        }, self.session)
        issue_title = 'new_issue'
        issue_description = 'new_issue_description'
        # Success Case
        result, log = discussion_new.new_discussion_core(
            session = self.session,
            log = regular_log.default(),
            member = None,
            project = job.project,
            title = issue_title,
            description = issue_description
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(log['error'].keys()), 0)
        # Error Case
        result, log = discussion_new.new_discussion_core(
            session = self.session,
            log = regular_log.default(),
            member = None,
            project = job.project.project_string_id,
            title = None,
            description = issue_description
        )

        self.assertIsNone(result)
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertIsNotNone(log['error'].get('title'))

