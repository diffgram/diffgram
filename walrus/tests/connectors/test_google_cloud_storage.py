from methods.regular.regular_api import *
from methods.connectors.google_cloud_storage_connector import GoogleCloudStorageConnector
from shared.database.input import Input
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import data_mocking


class TestGoogleCloudConnection(testing_setup.DiffgramBaseTestCase):
    """

        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestGoogleCloudConnection, self).setUp()
        self.project_string_id = 'my-google-test-project'
        project_data = data_mocking.create_project_with_context(
            {
                'project_string_id': self.project_string_id,
                'project_name': self.project_string_id,
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     'project_string_id': self.project_string_id
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        return
