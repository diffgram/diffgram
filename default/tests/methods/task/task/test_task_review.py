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


class TestTaskReview(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTaskReview, self).setUp()
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
            'name': 'my-test-job-{}'.format(1),
            'project': self.project,
            'allow_reviews': True
        }, self.session)
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        self.task = data_mocking.create_task({'name': 'test task', 'file': file, 'job': job, 'status': 'available'},
                                             self.session)
        self.task.add_reviewer(session = self.session, user = self.auth_api.member.user)
        self.task.add_reviewer(session = self.session, user = self.member.user)
        self.session.commit()

    def test_task_review_api(self):
        request_data = {
            'action': 'approve'
        }
        endpoint = "/api/v1/task/{}/review".format(self.task.id)
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        auth_api.member.user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'member_id': self.member.id
        }, self.session)
        self.task.add_reviewer(self.session, auth_api.member.user)
        self.session.commit()
        with self.client.session_transaction() as session:
            session['user_id'] = make_secure_val(auth_api.member.user.id)
            credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')

        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['task']['status'], 'complete')

        # 400 Case
        request_data = {
            'action': 'wrong_value'
        }
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 400)

    def test_task_review_core(self):
        # Approve & No comment case
        with patch.object(task_complete, 'task_complete') as mock:
            task_review.task_review_core(
                session = self.session,
                task_id = self.task.id,
                action = 'approve',
                member = self.member,
                comment_text = None
            )
            mock.assert_called_once_with(
                session = self.session,
                task = self.task,
                new_file = self.task.file,
                project = self.task.project,
                member = self.member,
                post_review = True
            )
        # Assert return
        result = task_review.task_review_core(
            session = self.session,
            task_id = self.task.id,
            action = 'approve',
            member = self.member,
            comment_text = None
        )
        self.assertEqual(result['id'], self.task.id)
        self.assertEqual(result['status'], TASK_STATUSES['complete'])

        # Approve & comment case
        with patch.object(task_complete, 'task_complete') as mock:
            with patch.object(DiscussionComment, 'new', return_value = 'discussion_comment_result') as new_mock:
                with patch.object(TaskEvent, 'generate_task_comment_event') as task_event_mock:
                    comment_text = 'comment'
                    result = task_review.task_review_core(
                        session = self.session,
                        task_id = self.task.id,
                        action = 'approve',
                        member = self.member,
                        comment_text = comment_text,
                    )
                    mock.assert_called_once_with(
                        session = self.session,
                        task = self.task,
                        new_file = self.task.file,
                        project = self.task.project,
                        member = self.member,
                        post_review = True
                    )

                    new_mock.assert_called_once_with(
                        session = self.session,
                        content = comment_text,
                        member_created_id = self.member.id,
                        project_id = self.task.project.id,
                        user_id = self.member.user_id
                    )

                    task_event_mock.assert_called_once_with(
                        session = self.session,
                        task = self.task,
                        member = self.member,
                        comment = 'discussion_comment_result'
                    )

        # Request Changes Case & No comment case
        with patch.object(Task_Update, 'main') as mock:
            task_review.task_review_core(
                session = self.session,
                task_id = self.task.id,
                action = 'request_change',
                member = self.member,
                comment_text = None
            )
            mock.assert_called_once()

        result = task_review.task_review_core(
            session = self.session,
            task_id = self.task.id,
            action = 'request_change',
            member = self.member,
            comment_text = None
        )
        mock.assert_called_once()
        self.assertEqual(result['id'], self.task.id)
        self.assertEqual(result['status'], TASK_STATUSES['requires_changes'])
