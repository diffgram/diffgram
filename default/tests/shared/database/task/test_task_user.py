from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.task.task_user import TaskUser
from unittest.mock import patch
import analytics
import requests


class TestTaskUser(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskUser, self).setUp()
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

    def test_new(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        task_user = TaskUser.new(
            session = self.session,
            task_id = task1.id,
            user_id = self.member.user.id,
            relation = 'test'
        )

        self.assertEqual(task_user.task_id, task1.id)
        self.assertEqual(task_user.user_id, self.member.user.id)
        self.assertEqual(task_user.relation, 'test')

    def test_serialize(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        task_user = TaskUser.new(
            session = self.session,
            task_id = task1.id,
            user_id = self.member.user.id,
            relation = 'test'
        )

        result = task_user.serialize()

        self.assertEqual(result['task_id'], task1.id)
        self.assertEqual(result['user_id'], self.member.user.id)
        self.assertEqual(result['relation'], 'test')
