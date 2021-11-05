from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.task.task_event import TaskEvent
from unittest.mock import patch
from methods.task.task.task_update import Task_Update
import analytics
import requests


class TestTaskEvent(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskEvent, self).setUp()
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
            'project_string_id': 'myproject',
            'member_id': self.member.id
        }, self.session)

    def test_get_task_from_job_id(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        task2 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        with patch.object(Task, 'add_assignee') as mock_1:
            with patch.object(Task_Update, 'main') as mock_2:
                next_task = Task.get_task_from_job_id(
                    session = self.session,
                    job_id = job.id,
                    user = self.member.user,
                    direction = 'next',
                    assign_to_user = True,
                    skip_locked = True

                )
                mock_1.assert_called_once()
                mock_2.assert_called_once()

                self.assertEqual(task1.id, next_task.id)
