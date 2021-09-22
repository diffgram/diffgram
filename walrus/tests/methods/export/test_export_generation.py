from methods.regular.regular_api import *
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from unittest.mock import patch
import analytics
import requests
from walrus.methods.export import export_generation

class TestExportGeneration(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestExportGeneration, self).setUp()
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

    def test_new_external_export(self):
        # TODO: add tests.
        file = data_mocking.create_file({'project_id': self.project.id, 'type': 'image'}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        source_directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file.id, 'label_file_id': label_file.id},
            self.session
        )
        export = data_mocking.create_export({
            'description': 'test',
            'source': 'directory',
            'kind': 'Annotations',
            'file_comparison_mode': 'latest',
            'project_id': self.project.id,
            'working_dir_id': source_directory.id,
            'ann_is_complete': False
        }, self.session)
        self.session.commit()
        with patch.object(export_generation.data_tools, 'upload_from_string') as mock_1:
            result, export_data = export_generation.new_external_export(
                session = self.session,
                project = self.project,
                export_id = export.id,
                version = None,
                working_dir = source_directory,
                use_request_context = False
            )
            mock_1.asser_called_once()
            print('ressss', export_data)
            self.assertTrue(result)
            self.assertTrue('readme' in export_data)
            self.assertTrue('label_map' in export_data)
            self.assertTrue('export_info' in export_data)
            self.assertTrue('attribute_groups_reference' in export_data)
            self.assertTrue(file.id in export_data)
            self.assertEqual(len(export_data[file.id]['instance_list']), 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['x_min'], 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['x_max'], 10)
            self.assertEqual(export_data[file.id]['instance_list'][0]['y_min'], 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['y_max'], 10)
            self.assertEqual(export_data[file.id]['instance_list'][0]['label_file_id'], label_file.id)


    def test_new_external_export_from_tasks(self):
        """
        Create a new job
        Create a file and task
        Annotate on tasks
        Generate export from that job
        """

        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        file = data_mocking.create_file(
            {'project_id': self.project.id, 
             'type': 'image'}, self.session)

        task_1 = data_mocking.create_task({
            'name': 'task1',
            'job': job,
            'file': file
        }, self.session)

        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 
             'file_id': file.id, 
             'label_file_id': label_file.id},
            self.session
        )


        export = data_mocking.create_export({
            'description': 'test',
            'source': 'job',
            'kind': 'Annotations',
            'project_id': self.project.id,
            'job_id': job.id,
            'ann_is_complete': False,
            'file_comparison_mode': 'latest'
        }, self.session)

        with patch.object(
            export_generation.data_tools, 'upload_from_string') as mock_1:

            result, export_data = export_generation.new_external_export(
                session = self.session,
                project = self.project,
                export_id = export.id,
                use_request_context = False
            )

            mock_1.assert_called_once()

            print('result', export_data[file.id]['instance_list'])

            self.assertTrue(result)

            self.assertTrue('readme' in export_data)
            self.assertTrue('label_map' in export_data)
            self.assertTrue('export_info' in export_data)
            self.assertTrue('attribute_groups_reference' in export_data)
            self.assertTrue(file.id in export_data)
            self.assertEqual(len(export_data[file.id]['instance_list']), 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['x_min'], 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['x_max'], 10)
            self.assertEqual(export_data[file.id]['instance_list'][0]['y_min'], 1)
            self.assertEqual(export_data[file.id]['instance_list'][0]['y_max'], 10)
            self.assertEqual(export_data[file.id]['instance_list'][0]['label_file_id'], label_file.id)

