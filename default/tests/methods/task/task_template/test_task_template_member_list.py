from methods.regular.regular_api import RegularAPI
from default.tests.test_utils import TestingSetup
from shared.tests.test_utils import CommonActions, DataMocking
from base64 import b64encode
from methods.task.task_template.task_template_member_list import task_template_members_list_core
from unittest.mock import patch
from methods.task.task_template.job_pin import job_pin_core
from shared.utils.logging import DiffgramLogger
import flask
import json

class TestTaskTemplateMemberList(TestingSetup.DiffgramBaseTestCase):
    """
    Test cases for the task template member list API.
    """

    def setUp(self) -> None:
        super().setUp()
        project_data = DataMocking.create_project_with_context(
            {
                'users': [
                    {
                        'username': 'test_user',
                        'email': 'test@test.com',
                        'password': 'diffgram123',
                    }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.auth_api = CommonActions.create_project_auth(project=self.project, session=self.session)
        self.member = self.auth_api.member
        self.member_user = DataMocking.register_user(
            {
                'username': 'test_user',
                'email': 'test@test.com',
                'password': 'diffgram123',
                'project_string_id': self.project.project_string_id,
                'member_id': self.member.id
            },
            self.session
        )
        self.reviewer = DataMocking.register_user(
            {
                'username': 'test_use2r',
                'email': 'test2@test.com',
                'password': 'diffgram123',
                'project_string_id': self.project.project_string_id,
                'member_id': self.member.id
            },
            self.session
        )

    def test_task_template_members_list_api(self) -> None:
        # Create mock job.
        task_template = DataMocking.create_job(
            {
                'name': 'my-test-job',
                'project': self.project
            },
            self.session
        )

        task_template.attach_user_to_job(session=self.session, user=self.member_user, add_to_session=True)
        task_template.attach_user_to_job(session=self.session, user=self.reviewer, relation='reviewer', add_to_session=True)
        self.session.commit()

        request_data = {}

        endpoint = f"/api/v1/job/{task_template.id}/members-list"

        with self.client.session_transaction() as session:
            auth_api = CommonActions.create_project_auth(project=self.project, session=self.session)
            credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode(
                'utf-8')
            session['Authorization'] = credentials
            CommonActions.add_auth_to_session(session, self.project.users[0])

        response = self.client.get(
            endpoint,
            data=json.dumps(request_data),
            headers={
                'directory_id': str(task_template.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )

        if response.status_code != 200:
            DiffgramLogger.log(f"Error: {response.text}")

        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['assignees']), 1)
        self.assertEqual(data['assignees'][0]['id'], self.member_user.id)

        self.assertEqual(len(data['reviewers']), 1)
        self.assertEqual(data['reviewers'][0]['id'], self.reviewer.id)

    def test_task_template_members_list_core(self) -> None:
        task_template = DataMocking.create_job(
            {
                'name': 'my-test-job',
                'project': self.project
            },
            self.session
        )

        task_template.attach_user_to_job(session=self.session, user=self.member_user)
        task_template.attach_user_to_job(session=self.session, user=self.reviewer, relation='reviewer')
        self.session.commit()

        result, log = task_template_members_list_core(session=self.session,
                                                      job_id=task_template.id,
                                                      log=RegularAPI.default_log())

        self.assertTrue('assignees' in result)
        self.assertTrue('reviewers' in result)
        self.assertEqual(len(result['assignees']), 1)
        self.assertEqual(result['assignees'][0]['id'], self.member_user.id)

        self.assertEqual(len(result['reviewers']), 1)
        self.assertEqual(result['reviewers'][0]['id'], self.reviewer.id)
