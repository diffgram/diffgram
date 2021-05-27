from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.source_control.file import file_exists


class TestFileExists(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestFileExists, self).setUp()
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
    def test_file_list_exists_api(self):
        file1 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file2 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file3 = data_mocking.create_file({'project_id': self.project.id}, self.session)
        file_diff = data_mocking.create_file({'project_id': self.project2.id}, self.session)
        request_data = {
            'file_id_list': [file1.id, file2.id, file3.id]
        }

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')

        endpoint = "/api/v1/project/{}/file/exists".format(self.project.project_string_id)
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data.get('exists'))

        request_data = {
            'file_id_list': [file1.id, file2.id, file3.id, file_diff.id]
        }

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')

        endpoint = "/api/v1/project/{}/file/exists".format(self.project.project_string_id)
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data.get('exists'))