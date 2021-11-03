from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.task.task_event import TaskEvent
from unittest.mock import patch
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

    def test_serialize(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file, 'job_id': job.id}, self.session)
        task_event = data_mocking.create_task_event({
            'job_id': job.id,
            'project_id': self.project.id,
            'task_id': task.id,
            'member_created_id': self.member.id,
            'event_type': 'task_created'

        }, self.session)

        result = task_event.serialize()

        self.assertEqual(result['task_id'], task_event.task_id)
        self.assertEqual(result['job_id'], task_event.job_id)
        self.assertEqual(result['project_id'], task_event.project_id)
        self.assertEqual(result['member_created_id'], task_event.member_created_id)
        self.assertEqual(result['event_type'], task_event.event_type)

    def test_generate_task_creation_event(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file, 'job_id': job.id}, self.session)
        task_event = TaskEvent.generate_task_creation_event(self.session, task)

        result = task_event.serialize()

        self.assertEqual(result['task_id'], task_event.task_id)
        self.assertEqual(result['job_id'], task_event.job_id)
        self.assertEqual(result['project_id'], task_event.project_id)
        self.assertEqual(result['member_created_id'], task_event.member_created_id)
        self.assertEqual(result['event_type'], 'task_created')

    def test_generate_task_completion_event(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file, 'job_id': job.id}, self.session)
        task_event = TaskEvent.generate_task_completion_event(self.session, task)

        result = task_event.serialize()

        self.assertEqual(result['task_id'], task_event.task_id)
        self.assertEqual(result['job_id'], task_event.job_id)
        self.assertEqual(result['project_id'], task_event.project_id)
        self.assertEqual(result['member_created_id'], task_event.member_created_id)
        self.assertEqual(result['event_type'], 'task_completed')

    def test_generate_task_review_complete(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file, 'job_id': job.id}, self.session)
        task_event = TaskEvent.generate_task_review_complete_event(self.session, task)

        result = task_event.serialize()

        self.assertEqual(result['task_id'], task_event.task_id)
        self.assertEqual(result['job_id'], task_event.job_id)
        self.assertEqual(result['project_id'], task_event.project_id)
        self.assertEqual(result['member_created_id'], task_event.member_created_id)
        self.assertEqual(result['event_type'], 'task_review_complete')
