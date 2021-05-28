from methods.connectors.s3_connector import S3Connector
from tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.input import packet
from shared.database.input import Input
import json
from base64 import b64encode
import datetime


class TestS3Connector(testing_setup.DiffgramBaseTestCase):
    """
        Test cases for the S3Connector methods. This test case test if images are uploaded sucessfully to diffgram
        
        
    """

    def setUp(self):
        super(TestS3Connector, self).setUp()
        self.project_string_id = 'my-test-s3-project'

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

        auth_data = {
            'client_id': '1',
            'client_secret': '1'
        }
        config_data = {'project_string_id': self.project_string_id}
        self.s3conn = S3Connector(
            auth_data=auth_data,
            config_data=config_data,
        )
        self.s3conn.connect()
        self.s3conn.test_connection()

    def test_packet_endpoint_refactor(self):
        packet_data = {
            'media': {
                'url': 'https://thumbor.forbes.com/thumbor/250x382/https://blogs-images.forbes.com/dorothypomerantz/files/2011/09/Spongebob-squarepants.jpg?width=960',
                'type': 'image'
            }

        }
        created_input = packet.enqueue_packet(self.project_string_id,
                                              session=self.session,
                                              media_url=packet_data['media']['url'],
                                              media_type=packet_data['media']['type'],
                                              job_id=None,
                                              directory_id=None)
        self.session.commit()
        self.assertEqual(type(created_input), type(Input()))

    def test_s3_add_to_diffgram(self):
        created_input = self.s3conn.fetch_data({
            'action_type': 'fetch_object',
            'path': 'tests3connector/pablo/patrick.png',
            'bucket_name': '1',
            'event_data': {
                'request_user': 1,
                'date_time': datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
                'connection_id': -1
            }
        })

        self.assertEqual(type(created_input), type(Input()))

    def test_input_packet_endpoint(self):
        # TODO: PENDING
        request_data = {
            'media': {
                'url': 'https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/tesla-model-s-1563301327.jpg',
                'type': 'image'
            },
            'frame_packet_map': None,
            'instance_list': None,
            'job_id': None,
            'video_split_duration': None,

        }

        endpoint = "/api/walrus/v1/project/" + self.project_string_id + "/input/packet"
        auth_api = common_actions.create_project_auth(project=self.project, session=self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        self.assertTrue(response.status_code == 200)
