from methods.regular.regular_api import *  # Importing regular_api methods
from default.tests.test_utils import testing_setup  # Importing testing setup
from shared.tests.test_utils import common_actions, data_mocking  # Importing common actions and data mocking utilities
from base64 import b64encode  # Importing base64 encoding function
from methods.task.task import task_next_issue  # Importing task_next_issue method
from unittest.mock import patch  # Importing patch for mocking
import flask  # Importing Flask library
from shared.database.hashing_functions import make_secure_val  # Importing hashing function
from methods.task.task import task_review  # Importing task_review method
from shared.utils.task import task_complete  # Importing task_complete utility
from shared.database.discussion.discussion_comment import DiscussionComment  # Importing DiscussionComment class
from shared.database.task.task_event import TaskEvent  # Importing TaskEvent class
from shared.utils.task.task_update_manager import Task_Update  # Importing Task_Update class
from shared.database.task.task import TASK_STATUSES  # Importing task statuses
from methods.task.task.task_user_remove import task_user_remove_core  # Importing task_user_remove_core method

class TestTasUserRemove(testing_setup.DiffgramBaseTestCase):
    """
    Test case class for testing task user removal functionality
    """

    def setUp(self):
        """
        Set up test environment by creating a project, task, and related objects
        """
        super(TestTasUserRemove, self).setUp()
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
        # Assigning variables for project, relation, auth_api, member, and task
        self.relation = 'assignee'
        self.project = project_data['project']
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)
        # Creating job, file, and task
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': True
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                             self.session)

    def test_api_task_user_remove(self):
        """
        Test task user removal API
        """
        request_data = {
            'relation': self.relation,
            'user_id_list': [self.member.user_id]
        }
        # Adding reviewer to the task and storing the relation
        relation = self.task.add_reviewer(session = self.session, user = self.member.user)
        endpoint = f"/api/v1/project/{self.project.project_string_id}/task/{self.task.id}/user/remove"
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)

        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')

        # Sending a POST request to the task user removal API
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )

        # Asserting the response status code and parsing the JSON data
        data = response.json
        self.assertEqual(response.status_code, 200)

    def test_task_user_remove_core(self):
        """
        Test task_user_remove_core method
        """
        result, log = task_user_remove_core(
            session = self.session,
            task_id = self.task.id,
            user_id_list = [self.member.user_id],
            relation = self.relation,
            project_string_id = self.project.project_string_id,
            log = regular_log.default()
        )

        # Asserting the result and log
        self.assertTrue(result)
        self.assertEqual(len(log['error'].keys()), 0)
