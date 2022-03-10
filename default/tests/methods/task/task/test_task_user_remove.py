from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.task.task import task_next_issue
from unittest.mock import patch
import flask
from shared.database.hashing_functions import make_secure_val
from methods.task.task import task_review
from shared.utils.task import task_complete
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.database.task.task_event import TaskEvent
from shared.utils.task.task_update_manager import Task_Update
from shared.database.task.task import TASK_STATUSES
from methods.task.task.task_user_remove import task_user_remove_core


class TestTasUserRemove(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
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
        job = data_mocking.create_job({
            'name': f"my-test-job-{1}",
            'project': self.project,
            'allow_reviews': True
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                             self.session)

    def test_api_task_user_remove(self):
        request_data = {
            'relation': self.relation,
            'user_id_list': [self.member.user_id]
        }
        relation = self.task.add_reviewer(session = self.session, user = self.member.user)
        endpoint = f"/api/v1/project/{self.project.project_string_id}/task/{self.task.id}/user/remove"
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)

        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )

        data = response.json
        self.assertEqual(response.status_code, 200)

    def test_task_user_remove_core(self):
        result, log = task_user_remove_core(
            session = self.session,
            task_id = self.task.id,
            user_id_list = [self.member.user_id],
            relation = self.relation,
            project_string_id = self.project.project_string_id,
            log = regular_log.default()
        )

        self.assertTrue(result)
        self.assertEqual(len(log['error'].keys()), 0)
