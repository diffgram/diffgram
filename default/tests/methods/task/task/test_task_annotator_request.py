from methods.regular.regular_api import *
from tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from unittest.mock import patch
from methods.task.task.task_annotator_request import get_next_task_by_project
import methods.task.task.task_annotator_request as task_annotator_request


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
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                             self.session)

    def test_get_next_task_by_project(self):
        self.member.user.last_task_id = None
        self.member.user.last_task = None
        self.session.add(self.member.user)
        self.session.commit()

        with patch.object(Task, 'get_last_task', return_value = None) as mock_1:
            with patch.object(Task, 'request_next_task_by_project', return_value = self.task) as mock_2:
                task_result = get_next_task_by_project(
                    session = self.session,
                    user = self.member.user,
                    project = self.project
                )

                self.assertIsNotNone(task_result)
                self.assertEqual(task_result, self.task)
                mock_1.assert_called_once()
                mock_2.assert_called_once()

    def test_get_next_task_by_job(self):
        self.member.user.last_task_id = None
        self.member.user.last_task = None
        self.session.add(self.member.user)
        self.session.commit()

        with patch.object(Task, 'get_last_task', return_value = None) as mock_1:
            with patch.object(task_annotator_request, 'recursively_get_next_available',
                              return_value = self.task) as mock_2:
                with patch.object(self.task, 'add_assignee',
                                  return_value = self.task) as mock_3:
                    task_result = get_next_task_by_project(
                        session = self.session,
                        user = self.member.user,
                        project = self.project
                    )

                    self.assertIsNotNone(task_result)
                    self.assertEqual(task_result.id, self.task.id)
                    mock_1.assert_called_once()
