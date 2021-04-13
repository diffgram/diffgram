from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import data_mocking, common_actions
from shared.utils.source_control.file import file_transfer_core




class TestFileTransferCore(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestFileTransferCore, self).setUp()
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
        self.project = self.project_data['project']
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member

    def test_file_transfer_core(self):
        # Mock data
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        source_directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        destination_directory = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)

        destination_directory_2 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)

        # Test Move
        result = file_transfer_core.file_transfer_core(
            session = self.session,
            source_directory = source_directory,
            destination_directory = destination_directory,
            transfer_action = 'move',
            file = file,
            log = regular_log.default(),
            member = self.member
        )
        self.assertEqual(len(result['error'].keys()), 0)

        # Test not existing file link case.
        result = file_transfer_core.file_transfer_core(
            session = self.session,
            source_directory = destination_directory_2,
            destination_directory = destination_directory,
            transfer_action = 'move',
            file = file,
            log = regular_log.default(),
            member = self.member)
        self.assertIsNotNone(result.get('error').get('file_link'))
