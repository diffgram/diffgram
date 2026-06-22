from methods.regular.regular_api import *  # Import regular API methods
from default.tests.test_utils import testing_setup  # Import testing setup from default.tests
from shared.tests.test_utils import common_actions, data_mocking  # Import common actions and data mocking utilities
from base64 import b64encode  # Import base64 encoding function
from methods.task.task.task_list import task_list_core  # Import task list core methods
from unittest.mock import patch  # Import patch for mocking
import flask  # Import Flask web framework

class TestVideoView(testing_setup.DiffgramBaseTestCase):
    """
    Test class for VideoView.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        super(TestVideoView, self).setUp()  # Call the parent class's setUp method

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
        )  # Create a project with a user

        self.project = project_data['project']  # Set the created project as an attribute

    def test_get_video_frame_from_task(self):
        """
        Test getting video frames from a task.
        """
        # Create mock task
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project
        }, self.session)

        video_file = data_mocking.create_file({
            'project_id': self.project.id,
            'type': 'video'
        }, self.session)  # Create a video file

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
        }, self.session)  # Create a task

        request_data = {
            'frame_list': [1, 2, 3],
            'project_string_id': self.project.project_string_id,
            'mode_data': 'list'
        }  # Prepare request data

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
        )  # Send a POST request to the endpoint

        self.assertEqual(response.status_code, 200)  # Check the response status code
        self.assertEqual(len(response.json['url_list']), 3)  # Check the number of URLs in the response

        i = 1
        for elm in response.json['url_list']:
            self.assertEqual(elm['frame_number'], i)  # Check the frame number of each URL
            i += 1
