from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.task.task_template import task_template_launch_handler
from walrus.methods.task.task_template.task_template_launch_handler import AfterLaunchControl
from shared.database.task.job.job import Job
from shared.database.task.job.job_launch import JobLaunch

from unittest.mock import patch


class TestTaskTemplateLaunchHandler(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskTemplateLaunchHandler, self).setUp()
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

    def test_task_template_launch_core(self):
        # Create mock tasks
        label = data_mocking.create_label({
            'name': 'mylabel',

        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'type': "Normal",
        }, self.session)
        result = task_template_launch_handler.task_template_launch_core(self.session, job)
        self.assertEqual(result, job)
        result = task_template_launch_handler.task_template_launch_core(self.session, None)
        self.session.commit()
        self.assertEqual(result, False)
        job = Job.get_by_id(self.session, job_id=job.id)
        self.assertEqual(job.status, 'active')

    def test_task_template_new_normal(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'type': "Normal",
        }, self.session)
        # TODO: analyze if provision_root_tasks_is needed now.
        result = task_template_launch_handler.task_template_new_normal(self.session, job)
        self.session.commit()
        job = Job.get_by_id(self.session, job_id=job.id)
        self.assertEqual(job.status, 'active')

    def test_task_template_new_exam(self):
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'type': "Normal",
        }, self.session)
        # TODO: analyze if provision_root_tasks_is needed now.
        result = task_template_launch_handler.task_template_new_exam(self.session, job)
        self.session.commit()
        job = Job.get_by_id(self.session, job_id=job.id)
        self.assertEqual(job.status, 'active')


class TestTaskTemplateLauncherThread(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskTemplateLauncherThread, self).setUp()
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

    def test_launch_job(self):
        # Create mock tasks
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        attach_dir1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'type': "Normal",
            'attached_directories': [
                attach_dir1
            ]
        }, self.session)

        with patch.object(AfterLaunchControl, 'main', return_value=True) as launch_control_main:
            job_launch = data_mocking.create_job_launch({'job_id': job.id}, self.session)
            job_launch_queue = data_mocking.create_job_launch_queue_element({'job_launch_id': job_launch.id},
                                                                            self.session)

            launch_handler = task_template_launch_handler.TaskTemplateLauncherThread()
            launch_handler.launch_job(session=self.session, task_template_queue_element=job_launch_queue)
            self.session.commit()
            job_launch = JobLaunch.get_by_id(session=self.session, job_launch_id=job_launch.id)
            self.assertEqual(job_launch.status, 'completed')
            self.assertEqual(job_launch.job_launch_info, 'Job Launched Successfully.')
            launch_control_main.assert_called_once()

    def test_check_if_jobs_to_launch(self):
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        attach_dir1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'type': "Normal",
            'attached_directories': [
                attach_dir1
            ]
        }, self.session)

        launch_handler = task_template_launch_handler.TaskTemplateLauncherThread()
        job_launch = data_mocking.create_job_launch({'job_id': job.id}, self.session)
        job_launch_queue = data_mocking.create_job_launch_queue_element(
            {'job_launch_id': job_launch.id},
            self.session)
        with patch.object(task_template_launch_handler.TaskTemplateLauncherThread, 'launch_job', return_value=True) as launch_control_main:
            launch_handler.check_if_jobs_to_launch()
            launch_control_main.assert_called_once()
