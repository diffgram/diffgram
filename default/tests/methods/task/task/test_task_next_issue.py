from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task import task_next_issue
from unittest.mock import patch
import flask


class TestTaskNextIssue(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskNextIssue, self).setUp()
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

    def test_task_next_issue(self):
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        all_tasks = []
        for i in range(0, num_tasks):
            task = data_mocking.create_task({
                'name': f"task{i}",
                'job': job
            }, self.session)
            all_tasks.append(task)

        issue1 = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)
        issue1.attach_element(
            session = self.session,
            element = {'type': 'task', 'id': all_tasks[2].id}
        )
        issue2 = data_mocking.create_discussion({
            'title': 'test2',
            'description': 'test2',
            'project_id': self.project.id
        }, self.session)
        issue2.attach_element(
            session = self.session,
            element = {'type': 'task', 'id': all_tasks[4].id}
        )

        with self.client.session_transaction() as session:
            endpoint = f"/api/v1/task/{all_tasks[0].id}/next-task-with-issues"
            credentials = b64encode(f"{self.auth_api.client_id}:{self.auth_api.client_secret}".encode()).decode('utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data = json.dumps({}),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['task_id'], all_tasks[2].id)

    def test_test_task_next_issue_core(self):
        # Create mock tasks
        # Create mock tasks
        num_tasks = 5
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        all_tasks = []
        for i in range(0, num_tasks):
            task = data_mocking.create_task({
                'name': f"task{i}",
                'job': job
            }, self.session)
            all_tasks.append(task)

        issue1 = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'project_id': self.project.id
        }, self.session)
        issue1.attach_element(
            session = self.session,
            element = {'type': 'task','id': all_tasks[2].id}
        )
        issue2 = data_mocking.create_discussion({
            'title': 'test2',
            'description': 'test2',
            'project_id': self.project.id
        }, self.session)
        issue2.attach_element(
            session = self.session,
            element = {'type': 'task', 'id': all_tasks[4].id}
        )

        result = task_next_issue.task_next_issue_core(
            session = self.session,
            task_id = all_tasks[0].id
        )
