from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from shared.database.audio.audio_file import data_tools
from unittest.mock import patch
from shared.database.audio.audio_file import AudioFile


class TestAudioFile(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestAudioFile, self).setUp()
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

    def test_get_by_id(self):
        audio_file = data_mocking.create_audio_file({}, self.session)

        fetched_audio = AudioFile.get_by_id(session = self.session, id = audio_file.id)

        self.assertEqual(fetched_audio.id, audio_file.id)
        
    def test_serialize(self):
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

        result = audio_file.serialize()
        
        self.assertEqual(result['original_filename'], audio_file.original_filename)
        self.assertEqual(result['description'], audio_file.description)
        self.assertEqual(result['soft_delete'], audio_file.soft_delete)
        self.assertEqual(result['url_public'], audio_file.url_public)
        self.assertEqual(result['url_signed'], audio_file.url_signed)
        self.assertEqual(result['url_signed_blob_path'], audio_file.url_signed_blob_path)
        self.assertEqual(result['url_signed_expiry'], audio_file.url_signed_expiry)
        self.assertEqual(result['url_signed_expiry_force_refresh'], audio_file.url_signed_expiry_force_refresh)

    def test_regenerate_url(self):
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

        with patch.object(data_tools, 'build_secure_url', return_value='new_blob_url') as mock_1:
          audio_file.regenerate_url(session = self.session)
          self.assertEqual(audio_file.url_signed, 'new_blob_url')
          mock_1.asser_called_once()
