import uuid
import hashlib
from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.annotation import Annotation_Update
from unittest.mock import patch
from shared.database.image import Image
from shared import url_generation
from shared.data_tools_core import data_tools


class TestURLGeneration(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestURLGeneration, self).setUp()
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

        self.credentials = b64encode("{}:{}".format(self.auth_api.client_id,
                                                    self.auth_api.client_secret).encode()).decode('utf-8')

    def test_blob_regenerate_url(self):
        image = Image()

        # Case of no url signed created
        url_generation.blob_regenerate_url(blob_object = image,
                                           session = self.session,
                                           connection_id = None,
                                           bucket_name = None)

        self.assertIsNone(image.url_signed)
        self.assertIsNone(image.url_signed_thumb)
        image.url_signed_blob_path = 'some_path'
        image.url_signed_thumb_blob_path = 'some_path'

        with patch.object(data_tools, 'determine_if_should_regenerate_url', return_value = (True, 1)) as mock_2:
            with patch.object(data_tools, 'build_secure_url', return_value = 'some_url') as mock_3:
                url_generation.blob_regenerate_url(blob_object = image,
                                                   session = self.session,
                                                   connection_id = None,
                                                   bucket_name = None)
                self.assertEqual('some_url', image.url_signed)
                self.assertIsNotNone(image.url_signed_thumb)

    def test_default_url_regenerate(self):
        image = Image()
        image.url_signed_blob_path = 'test'
        image.url_signed_thumb_blob_path = 'test_thumb'
        with patch.object(data_tools, 'build_secure_url', return_value = 'some_url') as mock1:
            url_generation.default_url_regenerate(blob_object = image,
                                                  session = self.session,
                                                  new_offset_in_seconds = 1000, )
            self.assertEqual('some_url', image.url_signed)
            self.assertIsNotNone(image.url_signed_thumb)
            self.assertIsNotNone(image.url_signed_expiry)
            self.assertTrue(1000 + time.time() >= image.url_signed_expiry)
