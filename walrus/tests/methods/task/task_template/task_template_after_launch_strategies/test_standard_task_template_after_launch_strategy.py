from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.task.task_template import task_template_launch_handler
from walrus.methods.task.task_template.task_template_after_launch_strategies.standard_task_template_after_launch_strategy import \
    StandardTaskTemplateAfterLaunchStrategy
from shared.database.task.job.job import Job
from shared.database.task.task import Task
from shared.regular import regular_log
from shared.database.task.job.job_working_dir import JobWorkingDir

class TestStandardTaskTemplateAfterLaunchStrategy(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestStandardTaskTemplateAfterLaunchStrategy, self).setUp()
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

    def test_execute_after_launch_strategy(self):
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        attach_dir1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'status': 'active',
            'type': "Normal",
            'attached_directories': [
                attach_dir1
            ]
        }, self.session)
        strategy = StandardTaskTemplateAfterLaunchStrategy(
            task_template=job,
            session=self.session,
            log=regular_log.default()
        )
        strategy.execute_after_launch_strategy()
        self.session.commit()
        tasks_count = self.session.query(Task).filter(
            Task.job_id == job.id
        ).count()
        tasks = self.session.query(Task).filter(
            Task.job_id == job.id
        ).all()

        self.assertEqual(tasks_count, 1)
