from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import data_mocking
from shared.utils.task import task_file_observers
from unittest.mock import patch
from shared.regular import regular_methods


class TestTaskFileObservers(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskFileObservers, self).setUp()
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

    def test_job_observable_creation(self):
        project = self.project_data['project']
        completion_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)
        print('completion_dir', completion_dir.id)
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'completion_directory_id': completion_dir.id
        }, self.session)
        job_observable = task_file_observers.JobObservable(session = self.session,
                                                           log = {},
                                                           job = job)
        self.assertEqual(len(job_observable.dir_observer_list), 1)
        dir_observer = job_observable.dir_observer_list[0]
        self.assertEqual(dir_observer.directory.id, job.completion_directory_id)
        self.assertEqual(dir_observer.job_observable, job_observable)

    def test_job_observable_add_observer(self):
        project = self.project_data['project']
        job = data_mocking.create_job(
            {
                'project': project
            },
            session = self.session
        )
        new_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)
        job_observable = task_file_observers.JobObservable(session = self.session,
                                                           log = {},
                                                           job = job)
        dir_observer = task_file_observers.DirectoryJobObserver(
            session = self.session,
            log = {},
            directory = new_dir,
            job_observable = job_observable
        )
        job_observable.add_new_directory_observer(dir_observer)
        self.session.commit()
        self.session.flush()
        updated_job = self.session.query(Job).filter(Job.id == job.id).first()
        self.assertEqual(updated_job.completion_directory_id, new_dir.id)

    def test_job_observable_remove_observer(self):
        project = self.project_data['project']
        new_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'completion_directory_id': new_dir.id
            },
            session = self.session
        )

        job_observable = task_file_observers.JobObservable(session = self.session,
                                                           log = {},
                                                           job = job)

        dir_observer = task_file_observers.DirectoryJobObserver(
            session = self.session,
            log = {},
            directory = new_dir,
            job_observable = job_observable
        )
        job_observable._remove_observer(dir_observer)
        self.session.commit()
        self.session.flush()
        updated_job = self.session.query(Job).filter(Job.id == job.id).first()
        self.assertEqual(updated_job.completion_directory_id, None)

    def test_job_observable_remove_observer(self):
        project = self.project_data['project']
        new_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)
        job = data_mocking.create_job(
            {
                'project': project,
                'completion_directory_id': new_dir.id
            },
            session = self.session
        )

        job_observable = task_file_observers.JobObservable(session = self.session,
                                                           log = {},
                                                           job = job)

        dir_observer = task_file_observers.DirectoryJobObserver(
            session = self.session,
            log = {},
            directory = new_dir,
            job_observable = job_observable
        )
        job_observable._remove_observer(dir_observer)
        self.session.commit()
        self.session.flush()
        updated_job = self.session.query(Job).filter(Job.id == job.id).first()
        self.assertEqual(updated_job.completion_directory_id, None)

    def test_notify_task_completion(self):
        project = self.project_data['project']
        new_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)
        old_dir = data_mocking.create_directory({
            'project': project,
            'user': self.project_data['users'][0],
        }, self.session)

        job = data_mocking.create_job(
            {
                'project': project,
                'completion_directory_id': new_dir.id,
                'output_dir_action': 'copy'
            },
            session = self.session
        )
        file = data_mocking.create_file({'project_id': project.id}, self.session)
        task_1 = data_mocking.create_task({
            'name': 'task1',
            'job': job,
            'file': file,
            'incoming_directory_id': old_dir.id
        }, self.session)
        with patch.object(regular_methods, 'transmit_interservice_request_after_commit') as mock:
            job_observable = task_file_observers.JobObservable(session = self.session,
                                                               log = regular_log.default(),
                                                               job = job,
                                                               task = task_1)
            dir_observer = task_file_observers.DirectoryJobObserver(
                session = self.session,
                log = regular_log.default(),
                directory = new_dir,
                job_observable = job_observable
            )
            job_observable.add_new_directory_observer(dir_observer)
            job_observable.notify_all_observers(defer = False)
            self.session.commit()
            file_link = self.session.query(WorkingDirFileLink).filter(
                WorkingDirFileLink.working_dir_id == new_dir.id).all()
            mock.assert_called_once()
