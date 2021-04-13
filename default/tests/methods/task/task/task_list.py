from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task.task_list import task_list_core
from unittest.mock import patch
import flask


class TestTaskList(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskList, self).setUp()
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

    def __send_request_task_list(self, request_data):

        endpoint = "/api/v1/project/{}/task/list".format(self.project.project_string_id)

        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project=self.project, session=self.session)
            credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        return response

    def test_task_list_api(self):
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        all_tasks = []
        for i in range(0, num_tasks):
            task = data_mocking.create_task({
                'name': 'task{}'.format(i),
                'job': job
            }, self.session)
            all_tasks.append(task)
        request_data = {
            'job_id': job.id,
            'project_string_id': self.project.project_string_id,
            'mode_data': 'list'
        }

        response = self.__send_request_task_list(request_data = request_data)

        self.assertEqual(response.status_code, 200)
        new_session = sessionMaker.session_factory()
        self.assertEqual(len(response.json['task_list']), num_tasks)

        # Case for project and file_id filter.
        all_tasks = []
        num_tasks_file = 2
        file = data_mocking.create_file({
            'project_id': self.project.id
        }, self.session)
        for i in range(0, num_tasks_file):
            task = data_mocking.create_task({
                'name': 'task{}'.format(i),
                'job': job,
                'file': file
            }, self.session)
            all_tasks.append(task)
        request_data = {
            'project_string_id': self.project.project_string_id,
            'file_id': file.id,
            'mode_data': 'list'
        }

        response = self.__send_request_task_list(request_data = request_data)
        self.assertEqual(response.status_code, 200)
        task_data = response.json
        self.assertEqual(len(task_data['task_list']), 2)

        request_data = {
            'project_string_id': self.project.project_string_id,
            'project_id': self.project.id,
            'mode_data': 'list'
        }
        response = self.__send_request_task_list(request_data = request_data)
        self.assertEqual(response.status_code, 200)
        task_data = response.json
        self.assertEqual(len(task_data['task_list']), num_tasks_file + num_tasks)

    def test_job_view_core(self):
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(2),
            'project': self.project
        }, self.session)
        all_tasks = []
        for i in range(0, num_tasks):
            task = data_mocking.create_task({
                'name': 'task{}'.format(i),
                'job': job
            }, self.session)
            all_tasks.append(task)
        self.session.commit()
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            result = task_list_core(self.session,
                                    date_from=None,
                                    date_to=None,
                                    status="all",
                                    job_id=job.id,
                                    incoming_directory_id=None,
                                    project_id=None,
                                    file_id=None,
                                    mode_data='list')
        logger.info(result)
        print(self.session.query(Job).all(), len(self.session.query(Job).all()))
        self.assertEqual(len(result), num_tasks)
