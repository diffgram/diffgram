from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task import task_next_issue
from unittest.mock import patch
import flask
from methods.task.task.task_annotator_request import get_next_task_by_project


class TestTaskAnnotatorRequest(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskAnnotatorRequest, self).setUp()
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
            'project_string_id': 'myproject',
            'member_id': self.member.id
        }, self.session)

    def test_get_next_task_by_project(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        task2 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        with patch.object(Task, 'get_last_task', return_value = None) as mock_1:
            with patch.object(Task, 'request_next_task_by_project') as mock_2:
                task_result = get_next_task_by_project(
                    session = self.session,
                    user = self.member.user,
                    project = self.project
                )

                self.assertIsNotNone(task_result)
                mock_1.assert_called_once()
                mock_2.assert_called_once()
