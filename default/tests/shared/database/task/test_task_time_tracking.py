from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.task.task_time_tracking import TaskTimeTracking
from unittest.mock import patch
import analytics
import requests


class TestTaskTimeTracking(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskTimeTracking, self).setUp()
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

    def test_get_global_record_from_status_record(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        record = TaskTimeTracking.new_or_update(
            session = self.session,
            project_id = self.project.id,
            task_id = task1.id,
            job_id = job.id,
            file_id = file.id,
            time_spent = 300,
            status = 'test',
            user_id = self.member.user.id,
            parent_file_id = file.id

        )

        self.session.commit()
        global_record = TaskTimeTracking.get_global_record_from_status_record(
            session = self.session,
            status_record = record
        )

        self.assertIsNotNone(global_record)
        self.assertIsNone(global_record.status)
        self.assertEqual(record.time_spent, global_record.time_spent)
        self.assertNotEqual(global_record.id, record.id)
        record2 = TaskTimeTracking.new_or_update(
            session = self.session,
            project_id = self.project.id,
            task_id = task1.id,
            job_id = job.id,
            file_id = file.id,
            time_spent = 550,
            status = 'test2',
            user_id = self.member.user.id,
            parent_file_id = file.id

        )
        self.session.commit()
        global_record = TaskTimeTracking.get_global_record_from_status_record(
            session = self.session,
            status_record = record
        )
        self.assertNotEqual(record.time_spent, global_record.time_spent)
        self.assertEqual(record.time_spent + record2.time_spent, global_record.time_spent)

    def test_new(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        record = TaskTimeTracking.new_or_update(
            session = self.session,
            project_id = self.project.id,
            task_id = task1.id,
            job_id = job.id,
            file_id = file.id,
            time_spent = 300,
            status = 'test',
            user_id = self.member.user.id,
            parent_file_id = file.id

        )
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'test')
        self.assertEqual(record.job_id, job.id)
        self.assertEqual(record.file_id, file.id)
        self.assertEqual(record.task_id, task1.id)
        self.assertEqual(record.parent_file_id, file.id)
        global_record = TaskTimeTracking.get_global_record_from_status_record(
            session = self.session,
            status_record = record
        )

        self.assertIsNotNone(global_record)
        self.assertIsNone(global_record.status)
        self.assertEqual(record.time_spent, global_record.time_spent)
        self.assertNotEqual(global_record.id, record.id)

    def test_serialize(self):
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task1 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)

        record = TaskTimeTracking.new_or_update(
            session = self.session,
            project_id = self.project.id,
            task_id = task1.id,
            job_id = job.id,
            file_id = file.id,
            time_spent = 300,
            status = 'test',
            user_id = self.member.user.id,
            parent_file_id = file.id

        )

        serilized_data = record.serialize()

        self.assertEqual(serilized_data['task_id'], task1.id)
        self.assertEqual(serilized_data['job_id'], job.id)
        self.assertEqual(serilized_data['project_id'], self.project.id)
        self.assertEqual(serilized_data['file_id'], file.id)
        self.assertEqual(serilized_data['parent_file_id'], file.id)
        self.assertEqual(serilized_data['status'], 'test')
