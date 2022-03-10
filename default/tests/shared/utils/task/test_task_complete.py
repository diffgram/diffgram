from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.utils.task import task_complete
from shared.database.task.task import TASK_STATUSES
from shared.utils.task import task_assign_reviewer
from shared.utils.task.task_update_manager import Task_Update
from unittest.mock import patch


class TestSyncEventsManager(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestSyncEventsManager, self).setUp()
        self.project_data = data_mocking.create_project_with_context(
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
        self.project = self.project_data['project']
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)

    def test_task_complete(self):
        # Create mock tasks
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file}, self.session)
        task.job.stat_count_tasks = 0
        task.job.stat_count_complete = 0
        task_complete.task_complete(session = self.session, task = task, new_file = task.file, project = self.project,
                                    member = self.member)

        self.assertEqual(task.status, TASK_STATUSES['complete'])
        # Now job should have +1 in completed col
        self.assertEqual(task.job.stat_count_complete, 1)

        task_complete.task_complete(session = self.session, task = task, new_file = task.file, project = self.project,
                                    member = self.member)
        # Count should still be one since task has already been completed.
        self.assertEqual(task.job.stat_count_complete, 1)

        # Test review mode
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': True
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task2 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        task_complete.task_complete(session = self.session,
                                    task = task2,
                                    new_file = task2.file,
                                    project = self.project,
                                    member = self.member)

        # Test Auto Assign call
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': True,
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task3 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        with patch.object(task_assign_reviewer, 'auto_assign_reviewer_to_task') as auto_assign_mock:
            with patch.object(task_complete, 'send_to_review_randomly') as send_to_review_mock:
                task_complete.task_complete(session = self.session,
                                            task = task3,
                                            new_file = task3.file,
                                            project = self.project,
                                            member = self.member)
                auto_assign_mock.asser_called_once_with(session = self.session, task = task)
                send_to_review_mock.assert_called_once()

        task_complete.task_complete(session = self.session,
                                    task = task3,
                                    new_file = task3.file,
                                    project = self.project,
                                    member = self.member)
        self.assertEqual(task3.status, TASK_STATUSES['review_requested'])

        # Test Auto Assign call with reviewer
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': True
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task4 = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                         self.session)
        job.update_reviewer_list(
            session = self.session,
            reviewer_list_ids = [self.member.id],
            log = regular_log.default()
        )

        task_complete.task_complete(session = self.session,
                                    task = task4,
                                    new_file = task4.file,
                                    project = self.project,
                                    member = self.member)
        auto_assign_mock.asser_called_once_with(session = self.session, task = task)
        self.assertEqual(task4.status, TASK_STATUSES['in_review'])

    def test_cost_per_task(self):
        result = task_complete.cost_per_task(5, 10)
        self.assertEqual(result, 55)

    def test_merge_task(self):
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        original_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        completion_dir = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [original_file]
        }, self.session)
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'completion_directory_id': completion_dir.id
        }, self.session)

        task = data_mocking.create_task({'name': 'test task',
                                         'file': file,
                                         'job': job,
                                         'file_original': original_file}, self.session)
        task_complete.merge_task(self.session, job, task)
        self.session.commit()
        file_link = self.session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == task.job.completion_directory_id,
            WorkingDirFileLink.file_id == task.file_id
        ).all()
        self.assertEqual(len(file_link), 1)

    def test_send_to_review_randomly(self):
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        original_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
        }, self.session)
        task = data_mocking.create_task({'name': 'test task',
                                         'file': file,
                                         'job': job,
                                         'file_original': original_file}, self.session)

        manager = Task_Update(
            session = self.session,
            task = task
        )
        with patch.object(task_assign_reviewer, 'auto_assign_reviewer_to_task') as mock:
            result = task_complete.send_to_review_randomly(
                session = self.session,
                task = task,
                task_update_manager = manager
            )
            mock.assert_called_once_with(session = self.session, task = task)


        self.assertFalse(result)
