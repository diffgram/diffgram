from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_comment_new
from unittest.mock import patch
import flask


class TeseFileCacheRegen(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseFileCacheRegen, self).setUp()
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

    def test_api_file_cache_regen(self):
        # Create mock tasks

        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': file.id, 'label_file_id': label_file.id},
            self.session
        )
        serialized_instances = [instance1.serialize_with_label(), instance2.serialize_with_label()]
        # Image case
        request_data = {}
        self.assertIsNone(file.cache_dict.get('instance_list'))
        endpoint = "/api/v1/project/{}/file/{}/regenerate-cache".format(self.project.project_string_id, file.id)
        credentials = b64encode("{}:{}".format(
            self.auth_api.client_id,
            self.auth_api.client_secret).encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'Authorization': 'Basic {}'.format(credentials)
            }

        )
        data = response.json
        print(data)
        self.assertEqual(response.status_code, 200)
        session2 = sessionMaker.session_factory()
        file_with_cache = File.get_by_id(session2, file_id = file.id)
        ids = [x['id'] for x in file_with_cache.cache_dict['instance_list']]
        self.assertTrue(instance1.id in ids)
        self.assertTrue(instance2.id in ids)

        # Video case
        video_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': video_file.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': video_file.id, 'label_file_id': label_file.id},
            self.session
        )
        # No frame provided case
        request_data = {}
        self.assertIsNone(video_file.cache_dict.get('instance_list'))
        endpoint = "/api/v1/project/{}/file/{}/regenerate-cache".format(self.project.project_string_id, video_file.id)
        credentials = b64encode("{}:{}".format(
            self.auth_api.client_id,
            self.auth_api.client_secret).encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'Authorization': 'Basic {}'.format(credentials)
            }

        )
        data = response.json
        print(data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('error' in data['log'])
        self.assertTrue('frame_number' in data['log']['error'])

        # Frame provided case
        video_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'video'}, self.session)
        frame_file = data_mocking.create_file({'project_id': self.project.id, 'type': 'frame', 'video_parent_file_id': video_file.id, 'frame_number': 54}, self.session)
        label_file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': frame_file.id, 'label_file_id': label_file.id},
            self.session
        )
        instance2 = data_mocking.create_instance(
            {'x_min': 1, 'x_max': 10, 'y_min': 1, 'y_max': 10, 'file_id': frame_file.id, 'label_file_id': label_file.id},
            self.session
        )
        request_data = {
            'frame_number': 54
        }
        self.assertIsNone(frame_file.cache_dict.get('instance_list'))
        endpoint = "/api/v1/project/{}/file/{}/regenerate-cache".format(self.project.project_string_id, frame_file.id)
        credentials = b64encode("{}:{}".format(
            self.auth_api.client_id,
            self.auth_api.client_secret).encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'Authorization': 'Basic {}'.format(credentials)
            }

        )
        data = response.json
        print(data)
        self.assertEqual(response.status_code, 200)
        session2 = sessionMaker.session_factory()
        file_with_cache = File.get_by_id(session2, file_id = frame_file.id)
        ids = [x['id'] for x in file_with_cache.cache_dict['instance_list']]
        self.assertTrue(instance1.id in ids)
        self.assertTrue(instance2.id in ids)

