from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.task.task_template.task_template_after_launch_strategies.scale_ai_task_template_after_launch_strategy import \
    ScaleAITaskTemplateAfterLaunchStrategy
from shared.database.task.task import Task
from shared.regular import regular_log
from shared.database.external.external import ExternalMap
from unittest.mock import patch
from shared.regular.regular_methods import commit_with_rollback


class TestScaleAITaskTemplateAfterLaunchStrategy(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestScaleAITaskTemplateAfterLaunchStrategy, self).setUp()
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
        connection = data_mocking.create_connection({
            'name': 'test',
            'integration_name': 'scale_ai',
            'project_id': self.project.id
        }, self.session)

        job = data_mocking.create_job({
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'status': 'active',
            'type': "Normal",
            'attached_directories': [
                attach_dir1
            ],
            'interface_connection_id': connection.id
        }, self.session)

        strategy = ScaleAITaskTemplateAfterLaunchStrategy(
            task_template=job,
            session=self.session,
            log=regular_log.default()
        )
        with patch.object(ScaleAITaskTemplateAfterLaunchStrategy, 'create_scale_ai_project',
                          return_value={'id': '123', 'name': 'scaleaitest'}):
            strategy.execute_after_launch_strategy()
            commit_with_rollback(self.session)
            tasks_count = self.session.query(Task).filter(
                Task.job_id == job.id
            ).count()
            tasks = self.session.query(Task).filter(
                Task.job_id == job.id
            ).all()
            self.assertEqual(tasks_count, 1)

            external_maps = ExternalMap.get(
                session=self.session,
                job_id=job.id,
                diffgram_class_string='task_template',
                connection_id=connection.id,
                type=connection.integration_name
            )

            self.assertNotEqual(external_maps, None)
