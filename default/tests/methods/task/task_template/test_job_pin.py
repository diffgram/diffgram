from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from unittest.mock import patch
from methods.task.task_template.job_pin import job_pin_core
from shared.utils.logging import DiffgramLogger
import flask


class TestJobPin(testing_setup.DiffgramBaseTestCase):
    """
        Test cases for pinning a job.
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestJobPin, self).setUp()
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

    def test_job_pin_api(self):
        # Create mock job.
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        request_data = {}

        endpoint = f"/api/v1/job/{job.id}/pin"

        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(job.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['job']['is_pinned'], True)

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(job.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['job']['is_pinned'], False)

    def test_job_pin_core(self):
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        job_result = job_pin_core(self.session, job_id = job.id)

        self.assertTrue(job_result['is_pinned'])

        job_result = job_pin_core(self.session, job_id = job.id)

        self.assertFalse(job_result['is_pinned'])
