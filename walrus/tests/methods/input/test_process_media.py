import tempfile
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.input import process_media
from methods.input.process_media import imwrite
from unittest.mock import patch
from shared.regular import regular_log
import numpy as np
from shared.settings import settings
from shared.database.source_control.file import File


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

        for extension in [".jpg", ".jpeg", ".png", ".webp"]:
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

        input_type = ''
        for extension in [".mp3", ".wav", ".flac"]:
            result = process_media.Process_Media.determine_media_type(
                input_type = input_type,
                extension = extension,
                allow_csv = allow_csv
            )
            self.assertEqual(result, 'audio')

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
        temp = open("myfile2.png", "w")
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
                mock1.assert_called_with(new_temp_filename, np.asarray(pm.raw_numpy_image), compress_level = 2)
                mock2.assert_called_with(temp_local_path = new_temp_filename,
                                         blob_path = pm.new_image.url_signed_blob_path,
                                         content_type = "image/jpg")

        # Test JPG Files
        temp = open("myfile3.png", "w")
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
                self.assertEqual(mock1.call_count, 0)
                mock2.assert_called_with(temp_local_path = new_temp_filename,
                                         blob_path = pm.new_image.url_signed_blob_path,
                                         content_type = "image/jpg")

        # Test BMP, TIF, TTF
        for file_extension in ['.bmp', '.tif', '.tiff']:
            temp = open("myfile4.png", "w")
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
                    mock1.assert_called_with(new_temp_filename, np.asarray(pm.raw_numpy_image), compress_level = 3)
                    mock2.assert_called_with(temp_local_path = new_temp_filename,
                                             blob_path = pm.new_image.url_signed_blob_path,
                                             content_type = "image/jpg")

    def test_route_based_on_media_type(self):
        log = regular_log.default()
        # Test PNG Files
        temp = open("myfile.png", "w")
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

        with patch.object(pm, 'process_one_image_file') as im_mock:
            input_obj.media_type = 'image'
            pm.route_based_on_media_type()
            im_mock.assert_called_once()
        with patch.object(pm, 'process_one_text_file') as text_mock:
            input_obj.media_type = 'text'
            pm.route_based_on_media_type()
            text_mock.assert_called_once()
        with patch.object(pm, 'process_one_audio_file') as audio_mock:
            input_obj.media_type = 'audio'
            pm.route_based_on_media_type()
            audio_mock.assert_called_once()
        with patch.object(pm, 'process_frame') as frame_mock:
            input_obj.media_type = 'frame'
            pm.route_based_on_media_type()
            frame_mock.assert_called_once()
        with patch.object(pm, 'process_sensor_fusion_json') as sensor_fusion_mock:
            input_obj.media_type = 'sensor_fusion'
            pm.route_based_on_media_type()
            sensor_fusion_mock.assert_called_once()
        with patch.object(pm, 'process_video') as video_mock:
            input_obj.media_type = 'video'
            pm.route_based_on_media_type()
            video_mock.assert_called_once()
        with patch.object(pm, 'process_csv_file') as csv_mock:
            input_obj.media_type = 'csv'
            pm.route_based_on_media_type()
            csv_mock.assert_called_once()

    def test_process_one_audio_file(self):
        log = regular_log.default()
        # Test PNG Files
        temp = open("myfile.mp3", "w")
        with open(temp.name, 'wb') as f:
            f.seek(63)
            f.write(b'\x01')
        input_obj = data_mocking.create_input(
            {
                'project_id': self.project.id,
                'extension': '.mp3',
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
        pm.working_dir_id = self.project.directory_default_id
        with patch.object(pm, 'save_raw_audio_file') as save_mock:
            with patch.object(process_media.File, 'new', return_value = process_media.File()) as im_new_file:
                pm.process_one_audio_file()
                save_mock.assert_called_once()
                im_new_file.assert_called_once()

        self.assertEqual(pm.input.status, 'success')
        self.assertEqual(pm.input.percent_complete, 100)
        self.assertIsNotNone(pm.input.time_completed)

    def test_save_raw_audio_file(self):
        log = regular_log.default()
        # Test PNG Files
        temp = open("myfile.png", "w")
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
        pm.project = self.project
        pm.new_audio_file = data_mocking.create_audio_file({}, session = self.session)
        with patch.object(process_media.data_tools, 'upload_to_cloud_storage') as mock:
            with patch.object(process_media.data_tools, 'build_secure_url', return_value = 'test_secure_url') as mock2:
                pm.save_raw_audio_file()
                mock.assert_called_once()
                self.assertEqual(pm.new_audio_file.url_signed_blob_path,
                                 '{}{}/{}'.format(settings.PROJECT_TEXT_FILES_BASE_DIR,
                                                  str(pm.project.id),
                                                  str(pm.new_audio_file.id)))
                mock2.assert_called_once()
                self.assertEqual(pm.new_audio_file.url_signed, 'test_secure_url')
