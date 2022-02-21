import tempfile
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.input import process_media
from methods.input.process_media import imwrite
from unittest.mock import patch
from shared.regular import regular_log
import numpy as np
from shared.settings import settings


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

    def test_save_raw_image_file(self):
        log = regular_log.default()
        # Test PNG Files
        temp = tempfile.NamedTemporaryFile(suffix = '.png')
        with open(temp.name, 'wb') as f:
            f.seek(63)
            f.write(b'\x01')
        input_obj = data_mocking.create_input(
            {
                'project_id': self.project.id,
                'extension': '.png',
                'temp_dir_path_and_filename': temp.name,
                'temp_dir': '/tmp'
            },
            session = self.session)
        pm = process_media.Process_Media(
            input_id = input_obj.id,
            input = input_obj,
            project_id = self.project.id,
            session = self.session,
        )
        pm.new_image = data_mocking.create_image({
            'original_filename': 'test_img.png'
        }, session = self.session)
        with patch.object(process_media, 'imwrite') as mock1:
            with patch.object(process_media.data_tools, 'upload_to_cloud_storage') as mock2:
                new_temp_filename = pm.save_raw_image_file()
                self.assertEqual(pm.new_image.url_signed_blob_path,
                                 f'{settings.PROJECT_IMAGES_BASE_DIR}{str(self.project.id)}/{str(pm.new_image.id)}')
                mock1.assert_called_with(new_temp_filename, np.asarray(pm.raw_numpy_image), compress_level = 2)
                mock2.assert_called_with(temp_local_path = new_temp_filename,
                                         blob_path = pm.new_image.url_signed_blob_path,
                                         content_type = "image/jpg")

        # Test JPG Files
        temp = tempfile.NamedTemporaryFile(suffix = '.jpg')
        with open(temp.name, 'wb') as f:
            f.seek(63)
            f.write(b'\x01')
        input_obj = data_mocking.create_input(
            {
                'project_id': self.project.id,
                'extension': '.jpg',
                'temp_dir_path_and_filename': temp.name,
                'temp_dir': '/tmp'
            },
            session = self.session)
        pm = process_media.Process_Media(
            input_id = input_obj.id,
            input = input_obj,
            project_id = self.project.id,
            session = self.session,
        )
        pm.new_image = data_mocking.create_image({
            'original_filename': 'test_img.jpg'
        }, session = self.session)
        with patch.object(process_media, 'imwrite') as mock1:
            with patch.object(process_media.data_tools, 'upload_to_cloud_storage') as mock2:
                new_temp_filename = pm.save_raw_image_file()
                self.assertEqual(pm.new_image.url_signed_blob_path,
                                 f'{settings.PROJECT_IMAGES_BASE_DIR}{str(self.project.id)}/{str(pm.new_image.id)}')
                self.assertEqual(mock1.call_count, 0)
                mock2.assert_called_with(temp_local_path = new_temp_filename,
                                         blob_path = pm.new_image.url_signed_blob_path,
                                         content_type = "image/jpg")


        # Test BMP, TIF, TTF
        for file_extension in ['.bmp', '.tif', '.tiff']:
            temp = tempfile.NamedTemporaryFile(suffix = file_extension)
            with open(temp.name, 'wb') as f:
                f.seek(63)
                f.write(b'\x01')
            input_obj = data_mocking.create_input(
                {
                    'project_id': self.project.id,
                    'extension': file_extension,
                    'temp_dir_path_and_filename': temp.name,
                    'temp_dir': '/tmp'
                },
                session = self.session)
            pm = process_media.Process_Media(
                input_id = input_obj.id,
                input = input_obj,
                project_id = self.project.id,
                session = self.session,
            )
            pm.new_image = data_mocking.create_image({
                'original_filename': f'test_img{file_extension}'
            }, session = self.session)
            with patch.object(process_media, 'imwrite') as mock1:
                with patch.object(process_media.data_tools, 'upload_to_cloud_storage') as mock2:
                    new_temp_filename = pm.save_raw_image_file()
                    self.assertEqual(pm.new_image.url_signed_blob_path,
                                     f'{settings.PROJECT_IMAGES_BASE_DIR}{str(self.project.id)}/{str(pm.new_image.id)}')
                    mock1.assert_called_with(new_temp_filename, np.asarray(pm.raw_numpy_image), compress_level = 3)
                    mock2.assert_called_with(temp_local_path = new_temp_filename,
                                             blob_path = pm.new_image.url_signed_blob_path,
                                             content_type = "image/jpg")
