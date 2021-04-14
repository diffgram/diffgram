from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.utils.task import task_complete


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

    def test_task_complete(self):
        # Create mock tasks
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        task = data_mocking.create_task({'name': 'test task', 'file': file}, self.session)
        task.job.stat_count_tasks = 1
        task_complete.task_complete(session=self.session, task=task, new_file=task.file, project=self.project)

        self.assertEqual(task.status, 'complete')
        # Now job should have +1 in completed col
        self.assertEqual(task.job.stat_count_complete, 1)
        self.assertEqual(task.job.status, 'complete')

        task_complete.task_complete(session=self.session, task=task, new_file=task.file, project=self.project)
        # Count should still be one since task has already been completed.
        self.assertEqual(task.job.stat_count_complete, 1)

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
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'completion_directory_id': completion_dir.id
        }, self.session)

        task = data_mocking.create_task({'name': 'test task',
                                         'file': file,
                                         'job': job,
                                         'file_original': original_file}, self.session)
        print('aasadsd', task.job, task.job.completion_directory_id)
        task_complete.merge_task(self.session, job, task)
        self.session.commit()
        file_link = self.session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == task.job.completion_directory_id,
            WorkingDirFileLink.file_id == task.file_id
        ).all()
        self.assertEqual(len(file_link), 1)

