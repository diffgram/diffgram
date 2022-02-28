from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.regular import regular_log
from methods.video import sequence_preview_create


class TestSequencePreviewCreate(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestSequencePreviewCreate, self).setUp()
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
        self.project = project_data['project']

    def test_api_create_sequence_preview(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        video_file = data_mocking.create_file({
            'project_id': self.project.id,
            'type': 'video'
        }, self.session)
        sequence = data_mocking.create_sequence({
            'label_file_id': label_file.id,
            'video_file_id': video_file.id,
            'cache_expiry': time.time() + 500000,
            'number': 1,

        }, self.session)
        video_file_bad = data_mocking.create_file({
            'project_id': self.project2.id,
            'type': 'video'
        }, self.session)
        preview_url = 'https://picsum.photos/200/300'
        instance = data_mocking.create_instance({
            'project_id': self.project.id,
            'type': 'box',
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0,
            'file_id': video_file.id,
            'soft_delete': False,
            'sequence_id': sequence.id,
            'preview_image_url': preview_url,
            'preview_image_url_expiry': 900000000,
        }, self.session)
        sequence.instance_preview_cache = {
            'id': instance.id,
            'file_id': sequence.video_file.id,
            'preview_image_url': preview_url,
        }
        self.session.commit()

        endpoint = "/api/project/{}/sequence/{}/create-preview".format(
            self.project.project_string_id,
            sequence.id,
        )
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps({}),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertTrue('result' in data)
        self.assertTrue('log' in data)
        self.assertFalse(len(data['log']['error'].keys()), 0)
        self.assertEqual(data['result']['instance_preview']['id'], instance.id)
        self.assertEqual(data['result']['instance_preview']['file_id'], video_file.id)
        self.assertEqual(data['result']['instance_preview']['preview_image_url'], preview_url)

        # Error case
        sequence2 = data_mocking.create_sequence({
            'label_file_id': label_file.id,
            'video_file_id': video_file_bad.id,
            'cache_expiry': time.time() + 500000,
            'number': 1,

        }, self.session)
        result, log = sequence_preview_create.create_sequence_preview_core(
            session = self.session,
            log = regular_log.default(),
            project = self.project,
            sequence_id = sequence2.id
        )
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertTrue('project_id' in log['error'])

    def test_create_sequence_preview_core(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        video_file = data_mocking.create_file({
            'project_id': self.project.id,
            'type': 'video'
        }, self.session)
        video_file_bad = data_mocking.create_file({
            'project_id': self.project2.id,
            'type': 'video'
        }, self.session)
        sequence = data_mocking.create_sequence({
            'label_file_id': label_file.id,
            'video_file_id': video_file.id,
            'cache_expiry': time.time() + 500000,
            'number': 1,

        }, self.session)

        sequence2 = data_mocking.create_sequence({
            'label_file_id': label_file.id,
            'video_file_id': video_file_bad.id,
            'cache_expiry': time.time() + 500000,
            'number': 1,

        }, self.session)

        preview_url = 'https://picsum.photos/200/300'
        instance = data_mocking.create_instance({
            'project_id': self.project.id,
            'type': 'box',
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0,
            'file_id': video_file.id,
            'soft_delete': False,
            'sequence_id': sequence.id,
            'preview_image_url': preview_url,
            'preview_image_url_expiry': 900000000,
        }, self.session)
        sequence.instance_preview_cache = {
            'id': instance.id,
            'file_id': sequence.video_file.id,
            'preview_image_url': preview_url,
        }
        self.session.commit()

        result, log = sequence_preview_create.create_sequence_preview_core(
            session = self.session,
            log = regular_log.default(),
            project = self.project,
            sequence_id = sequence.id
        )

        self.assertFalse(len(log['error'].keys()), 0)
        self.assertEqual(result['instance_preview']['id'], instance.id)
        self.assertEqual(result['instance_preview']['file_id'], video_file.id)
        self.assertEqual(result['instance_preview']['preview_image_url'], preview_url)

        # Error case
        result, log = sequence_preview_create.create_sequence_preview_core(
            session = self.session,
            log = regular_log.default(),
            project = self.project,
            sequence_id = sequence2.id
        )
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertTrue('project_id' in log['error'])
