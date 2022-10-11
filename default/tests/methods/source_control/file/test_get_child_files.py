from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.source_control.file import file_get_child_files


class TestGetChildFiles(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestGetChildFiles, self).setUp()
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

        project_data2 = data_mocking.create_project_with_context(
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
        self.project2 = project_data2['project']

    def test_api_file_get_child_files(self):
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'compound'}, self.session)
        file2 = data_mocking.create_file({'project_id': self.project.id,
                                          'parent_id': file1.id,
                                          'type': 'image',
                                          }, self.session)
        file3 = data_mocking.create_file({'project_id': self.project.id,
                                          'type': 'image',
                                          'parent_id': file1.id}, self.session)
        request_data = {
            'file_id_list': [file1.id, file2.id, file3.id]
        }

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')

        endpoint = f"/api/v1/project/{self.project.project_string_id}/file/{file1.id}/child-files"
        response = self.client.get(
            endpoint,
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get('child_files')), 2)

        child_files = data.get('child_files')
        child_files_id_list = [x['id'] for x in child_files]

        self.assertTrue(file2.id in child_files_id_list)
        self.assertTrue(file3.id in child_files_id_list)

    def test_get_child_files_core(self):
        file1 = data_mocking.create_file({'project_id': self.project.id, 'type': 'compound'}, self.session)
        file2 = data_mocking.create_file({'project_id': self.project.id,
                                          'parent_id': file1.id,
                                          'type': 'image',
                                          }, self.session)
        file3 = data_mocking.create_file({'project_id': self.project.id,
                                          'type': 'image',
                                          'parent_id': file1.id}, self.session)
        request_data = {
            'file_id_list': [file1.id, file2.id, file3.id]
        }

        child_files, log = file_get_child_files.get_child_files_core(
            session = self.session,
            project = self.project,
            parent_file_id = file1.id,
        )
        self.assertEqual(len(log.get('error').keys()), 0)

        child_files_id_list = [x['id'] for x in child_files]

        self.assertTrue(file2.id in child_files_id_list)
        self.assertTrue(file3.id in child_files_id_list)
