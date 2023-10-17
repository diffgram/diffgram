from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task.task_list import task_list_core
from unittest.mock import patch
import flask


class TestVideoView(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestVideoView, self).setUp()
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

    def test_get_video_frame_from_task(self):
        return # See https://github.com/diffgram/diffgram/issues/1560  
        # Create mock task
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)
        video_file = data_mocking.create_file({
            'project_id': self.project.id,
            'type': 'video'
        }, self.session)
        frames_list = []
        # Mock Frames
        for i in range(0, 10):
            frame = data_mocking.create_file({
                'project_id': self.project.id,
                'video_parent_file_id': video_file.id,
                'frame_number': i,
                'type': 'frame'
            }, self.session)
            frames_list.append(frame)

        task = data_mocking.create_task({
            'name': 'tasktest',
            'job': job,
            'file': video_file
        }, self.session)

        request_data = {
            'frame_list': [1, 2, 3],
            'project_string_id': self.project.project_string_id,
            'mode_data': 'list'
        }

        endpoint = f"/api/v1/task/{task.id}/video/single/{video_file.id}/frame-list/"
        with self.client.session_transaction() as session:
            auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            common_actions.add_auth_to_session(session, self.project.users[0])
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(job.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['url_list']), 3)
        i = 1
        for elm in response.json['url_list']:
            self.assertEqual(elm['frame_number'], i)
            i += 1
