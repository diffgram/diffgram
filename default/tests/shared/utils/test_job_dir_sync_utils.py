from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from unittest.mock import patch
from methods.task.task_template import job_new_or_update
from shared.utils import job_dir_sync_utils
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.regular.regular_methods import commit_with_rollback
from shared.utils.sync_events_manager import SyncEventManager


class TestJobDirSyncUtils(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestJobDirSyncUtils, self).setUp()
        # Create mock project/job.
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

    def test__add_file_into_job(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        log = regular_log.default()
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job
        )
        sync_manager._JobDirectorySyncManager__add_file_into_job(
            file,
            directory,
            create_tasks=True
        )
        commit_with_rollback(self.session)

        dir_link = self.session.query(WorkingDirFileLink).filter(WorkingDirFileLink.file_id == file.id,
                                                                 WorkingDirFileLink.working_dir_id == job.directory_id)
        self.assertTrue(dir_link.first() is not None)
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        self.assertTrue(task.first() is None)

        # If job has correct status task should be created.
        job.status = 'active'
        self.session.add(job)
        commit_with_rollback(self.session)

        sync_manager._JobDirectorySyncManager__add_file_into_job(
            file,
            directory,
            create_tasks=True
        )
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        self.assertTrue(task.first() is not None)
        commit_with_rollback(self.session)
        # Retest for case of an existing file/task.
        mngr = SyncEventManager.create_sync_event_and_manager(session=self.session, status='started')
        sync_manager._JobDirectorySyncManager__add_file_into_job(
            file,
            directory,
            create_tasks=True,
            sync_event_manager=mngr
        )
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        self.assertTrue(task.first() is not None)

    def test__sync_all_jobs_from_dir(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job1 = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        job2 = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file],
            'jobs_to_sync': {
                'job_ids': [job1.id, job2.id]
            }
        }, self.session)
        for job in [job1, job2]:
            job.update_attached_directories(self.session,
                                            [{'directory_id': directory.id, 'selected': 'sync'}]
                                            )
        log = regular_log.default()
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=None
        )
        sync_manager._JobDirectorySyncManager__sync_all_jobs_from_dir(
            file,
            directory,
            directory,
            create_tasks=True
        )

        dir_link = self.session.query(WorkingDirFileLink).filter(WorkingDirFileLink.file_id == file.id,
                                                                 WorkingDirFileLink.working_dir_id == job1.directory_id)

        dir_link2 = self.session.query(WorkingDirFileLink).filter(WorkingDirFileLink.file_id == file.id,
                                                                  WorkingDirFileLink.working_dir_id == job2.directory_id)
        self.assertTrue(dir_link.first() is not None)
        self.assertTrue(dir_link2.first() is not None)
        task1 = self.session.query(Task).filter(
            Task.job_id == job1.id
        )
        task2 = self.session.query(Task).filter(
            Task.job_id == job2.id
        )
        self.assertTrue(task1.first() is not None)
        self.assertTrue(task2.first() is not None)

    def test_remove_directory_from_all_attached_jobs(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)
        log = regular_log.default()
        dir_list = [
            {'directory_id': directory.id, 'nickname': directory.nickname, 'selected': 'sync'}
        ]
        job.update_attached_directories(self.session, dir_list, delete_existing=True)
        self.session.add(job)
        commit_with_rollback(self.session)
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job,
            directory=directory
        )
        sync_manager.remove_directory_from_all_attached_jobs(soft_delete=False)
        commit_with_rollback(self.session)
        self.session.flush()
        attachments = job.get_attached_dirs(self.session)
        self.assertEqual(len(attachments), 0)

    def test_remove_job_from_all_dirs(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)
        log = regular_log.default()
        dir_list = [
            {'directory_id': directory.id, 'nickname': directory.nickname, 'selected': 'sync'}
        ]
        job.update_attached_directories(self.session, dir_list, delete_existing=True)
        self.session.add(job)
        commit_with_rollback(self.session)
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job,
            directory=directory
        )
        sync_manager.remove_job_from_all_dirs(soft_delete=False)
        commit_with_rollback(self.session)
        self.session.flush()
        directory_attachments = self.session.query(JobWorkingDir).filter(
            JobWorkingDir.working_dir_id == directory.id).all()
        self.assertEqual(len(directory_attachments), 0)

    def test_create_task_from_file(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)
        log = regular_log.default()
        dir_list = [
            {'directory_id': directory.id, 'nickname': directory.nickname, 'selected': 'sync'}
        ]
        job.update_attached_directories(self.session, dir_list, delete_existing=True)
        self.session.add(job)
        commit_with_rollback(self.session)
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job,
        )
        sync_manager.create_task_from_file(file)
        commit_with_rollback(self.session)
        self.session.flush()
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        self.assertTrue(task.first() is not None)

    def test_add_file_to_all_jobs(self):
        project = self.project_data['project']
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)
        log = regular_log.default()
        dir_list = [
            {'directory_id': directory.id, 'nickname': directory.nickname, 'selected': 'sync'}
        ]
        job.update_attached_directories(self.session, dir_list, delete_existing=True)
        self.session.add(job)
        commit_with_rollback(self.session)
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job,
            directory=directory
        )
        sync_manager.add_file_to_all_jobs(file, create_tasks=True)
        commit_with_rollback(self.session)
        self.session.flush()
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        self.assertTrue(task.first() is not None)

    def test_create_file_links_for_attached_dirs(self):
        project = self.project_data['project']
        file1 = data_mocking.create_file({'project_id': project.id}, self.session)
        file2 = data_mocking.create_file({'project_id': project.id}, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'status': 'active'
            },
            session=self.session
        )
        directory1 = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file1],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)

        directory2 = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
            'files': [file2],
            'jobs_to_sync': {
                'job_ids': [job.id]
            }
        }, self.session)
        log = regular_log.default()
        dir_list = [
            {'directory_id': directory1.id, 'nickname': directory1.nickname, 'selected': 'sync'},
            {'directory_id': directory2.id, 'nickname': directory2.nickname, 'selected': 'sync'}
        ]
        job.update_attached_directories(self.session, dir_list, delete_existing=True)
        self.session.add(job)
        self.session.add(directory1)
        self.session.add(directory2)
        commit_with_rollback(self.session)
        sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            log=log,
            job=job,
        )
        sync_manager.create_file_links_for_attached_dirs(create_tasks=True)
        commit_with_rollback(self.session)
        self.session.flush()
        dir_link1 = self.session.query(WorkingDirFileLink).filter(WorkingDirFileLink.file_id == file1.id,
                                                                  WorkingDirFileLink.working_dir_id == job.directory_id)
        dir_link2 = self.session.query(WorkingDirFileLink).filter(WorkingDirFileLink.file_id == file2.id,
                                                                  WorkingDirFileLink.working_dir_id == job.directory_id)
        self.assertTrue(dir_link1.first() is not None)
        self.assertTrue(dir_link2.first() is not None)
        task = self.session.query(Task).filter(
            Task.job_id == job.id
        )
        task1 = self.session.query(Task).filter(
            Task.job_id == job.id,
            Task.file_id == file1.id
        )
        task2 = self.session.query(Task).filter(
            Task.job_id == job.id,
            Task.file_id == file2.id
        )
        self.assertEqual(len(task.all()), 2)
        self.assertTrue(task1.first() is not None)
        self.assertTrue(task2.first() is not None)
