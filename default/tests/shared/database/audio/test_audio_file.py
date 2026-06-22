from methods.regular.regular_api import *  # Importing all functions/classes from the regular_api module
from default.tests.test_utils import testing_setup  # Importing testing_setup from test_utils module
from shared.tests.test_utils import common_actions, data_mocking  # Importing common_actions and data_mocking from test_utils module
from base64 import b64encode  # Importing b64encode function for encoding data to base64

# Importing Member class from the member module in the auth package of the shared.database
from shared.database.auth.member import Member

# Importing DataToolsCore class from the data_tools_core module in the shared.data_tools package
from shared.data_tools_core import data_tools

# Importing Patch decorator from the unittest.mock module for mocking objects
from unittest.mock import patch

# Importing AudioFile class from the audio_file module in the audio package of the shared.database
from shared.database.audio.audio_file import AudioFile

class TestAudioFile(testing_setup.DiffgramBaseTestCase):
    """
    TestAudioFile class inherits from DiffgramBaseTestCase class.
    This class contains unit tests for the AudioFile class.
    """

    def setUp(self):
        """
        setUp method is called before each test method is executed.
        It initializes the session, creates a project, and sets up the required objects for testing.
        """
        super(TestAudioFile, self).setUp()

        # Creating a project with a user
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

        # Setting the project and project_data attributes
        self.project = project_data['project']
        self.project_data = project_data

        # Creating an auth_api object for the project
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)

        # Setting the member attribute
        self.member = self.auth_api.member

    def test_get_by_id(self):
        """
        Test case for the get_by_id method of the AudioFile class.
        It creates an audio file and fetches it using the get_by_id method.
        """
        audio_file = data_mocking.create_audio_file({}, self.session)

        fetched_audio = AudioFile.get_by_id(session = self.session, id = audio_file.id)

        self.assertEqual(fetched_audio.id, audio_file.id)

    def test_serialize(self):
        """
        Test case for the serialize method of the AudioFile class.
        It creates an audio file with test data and serializes it using the serialize method.
        """
        test_audio_data = {
            'original_filename': 'test123',
            'description': 'description123',
            'soft_delete': True,
            'url_public': 'url_public123',
            'url_signed': 'url_signed123',
            'url_signed_blob_path': 'url_signed_blob_path123',
            'url_signed_expiry': 5000,
            'url_signed_expiry_force_refresh': 1,
        }
        audio_file = data_mocking.create_audio_file(test_audio_data, self.session)

        result = audio_file.serialize(self.session)

        self.assertEqual(result['original_filename'], audio_file.original_filename)
        self.assertEqual(result['description'], audio_file.description)
        self.assertEqual(result['soft_delete'], audio_file.soft_delete)
        self.assertEqual(result['url_public'], audio_file.url_public)
        self.assertEqual(result['url_signed'], audio_file.url_signed)
        self.assertEqual(result['url_signed_blob_path'], audio_file.url_signed_blob_path)
        self.assertEqual(result['url_signed_expiry'], audio_file.url_signed_expiry)
        self.assertEqual(result['url_signed_expiry_force_refresh'], audio_file.url_signed_expiry_force_refresh)
