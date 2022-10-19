from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_new
from unittest.mock import patch
from shared.database.input import Input
import flask


class TestCompoundFileNew(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestCompoundFileNew, self).setUp()
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

    def test_api_file_compound_new(self):
        source_directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        request_data = {
            'name': 'testcompound.png',
            'directory_id': source_directory.id
        }
        endpoint = f"/api/v1/project/{self.project.project_string_id}/file/new-compound"
        credentials = b64encode("{}:{}".format(
            self.auth_api.client_id,
            self.auth_api.client_secret).encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'Authorization': f"Basic {credentials}"
            }

        )
        data = response.json
        file = data['file']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(file['original_filename'], request_data['name'])
        self.assertEqual(file['type'], 'compound')

        inputs = self.session.query(Input).filter(
            Input.file_id == file['id'],
            Input.type == 'from_compound'
        ).all()
        self.assertEqual(len(inputs), 1)
