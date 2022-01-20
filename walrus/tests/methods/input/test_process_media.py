from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.input import process_media
from unittest.mock import patch
from shared.regular import regular_log


class TestProcessMedia(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestProcessMedia, self).setUp()
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

    def test_determine_media_type(self):
        log = regular_log.default()
        input_type = ''
        extension = 'test'
        allow_csv = True

        result = process_media.Process_Media.determine_media_type(
            input_type = input_type,
            extension = extension,
            allow_csv = allow_csv
        )

        self.assertIsNone(result)

        for extension in [".jpg", ".jpeg", ".png"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'image')

        for extension in [".mp4", ".mov", ".avi", ".m4v", ".quicktime"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'video')

        for extension in [".txt"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'text')

        allow_csv = False
        for extension in [".csv"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, None)
        allow_csv = True
        for extension in [".csv"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'csv')

        input_type = 'from_sensor_fusion_json'
        for extension in [".json"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'sensor_fusion')

        input_type = 'other'
        for extension in [".json"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'existing_instances')