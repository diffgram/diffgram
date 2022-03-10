from shared.utils.task import task_complete
from methods.task.task.task_complete import task_complete_core
from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from unittest.mock import patch
from shared.database.task.task import TASK_STATUSES
from shared.database.hashing_functions import make_secure_val


class TestTaskComplete(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskComplete, self).setUp()
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
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': False
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                             self.session)
        self.task.add_reviewer(session = self.session, user = self.auth_api.member.user)
        self.task.add_reviewer(session = self.session, user = self.member.user)
        self.session.commit()

    def test_api_task_complete(self):
        request_data = {
            'action': 'approve'
        }
        endpoint = f"/api/v1/task/{self.task.id}/complete"
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        auth_api.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)
        with self.client.session_transaction() as session:
            session['user_id'] = make_secure_val(auth_api.member.user.id)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        self.task.add_assignee(self.session, auth_api.member.user)
        self.session.commit()
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
        self.assertEqual(data['task']['status'], 'complete')

    def test_task_complete_core(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': False
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                        self.session)
        result = task_complete_core(
            session = self.session,
            task_id = task.id,
            member = self.member

        )
        self.assertEqual(result['status'], TASK_STATUSES['complete'])
        with patch.object(task_complete, 'task_complete') as mock:
            task_complete_core(
                session = self.session,
                task_id = task.id,
                member = self.member

            )
            mock.assert_called_once_with(session = self.session,
                                         task = task,
                                         new_file = task.file,
                                         project = task.project,
                                         member = self.member,
                                         post_review = False
                                         )
