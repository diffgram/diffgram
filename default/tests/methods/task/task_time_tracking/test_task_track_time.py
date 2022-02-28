from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.hashing_functions import make_secure_val
from methods.task.task_time_tracking.task_track_time import track_time_core
import flask


class TestTaskTrackTime(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskTrackTime, self).setUp()
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
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)

    def test_api_task_track_time(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        request_data = {
            'file_id': file.id,
            'status': 'pending',
            'time_spent': 1500,
            'job_id': job.id,
        }
        task1.add_assignee(self.session, self.member.user)
        with self.client.session_transaction() as session:
            session['user_id'] = make_secure_val(self.auth_api.member.user.id)
            endpoint = f"/api/v1/task/{task1.id}/track-time"
            auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue('task_id' in data)
        self.assertTrue('job_id' in data)
        self.assertTrue('project_id' in data)
        self.assertTrue('time_spent' in data)
        self.assertTrue('user_id' in data)
        self.assertTrue('status' in data)
        self.assertEqual(data['task_id'], task1.id)
        self.assertEqual(data['job_id'], job.id)
        self.assertEqual(data['user_id'], self.auth_api.member.user.id)
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(data['project_id'], self.project.id)
        self.assertEqual(data['time_spent'], 1500)

    def test_track_time_core(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        result, log = track_time_core(
            session = self.session,
            project = self.project,
            task_id = task1.id,
            status = 'pending',
            job_id = job.id,
            file_id = file.id,
            user = self.member.user,
            time_spent = 333,
            parent_file_id = None,
            log = regular_log.default()
        )
        self.assertTrue('task_id' in result)
        self.assertTrue('job_id' in result)
        self.assertTrue('project_id' in result)
        self.assertTrue('time_spent' in result)
        self.assertTrue('user_id' in result)
        self.assertTrue('status' in result)
        self.assertEqual(result['task_id'], task1.id)
        self.assertEqual(result['job_id'], job.id)
        self.assertEqual(result['user_id'], self.auth_api.member.user.id)
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['project_id'], self.project.id)
        self.assertEqual(result['time_spent'], 333)
