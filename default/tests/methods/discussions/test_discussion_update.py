from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.discussions import discussion_update
from unittest.mock import patch
import flask


class TeseDiscussionUpdate(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseDiscussionUpdate, self).setUp()
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


    def test_update_discussion_web(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)

        instance = data_mocking.create_instance({
            'project_id': self.project.id,
            'type': 'box',
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0,
        }, self.session)
        discussion.attach_element(session = self.session, element = {
            'type': 'instance',
            'id': instance.id
        })
        job = data_mocking.create_job({
            'name': 'my-test-job',
            'project': self.project
        }, self.session)

        new_content = 'new content.'
        request_data = {
            'attached_elements': [{'type': 'job', 'id': job.id}],
            'description': new_content
        }
        endpoint = f"/api/v1/project/{self.project.project_string_id}/discussion/{discussion.id}/update"

        credentials = b64encode(f"{self.auth_api.client_id}:{self.auth_api.client_secret}".encode()).decode('utf-8')
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        print(data, 'lll')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('discussion' in data)
        self.assertEqual(data['discussion']['description'], new_content)
        # Just one should be here, as attached job should be ignored.
        self.assertEqual(len(data['discussion']['attached_elements']), 1)
        job_attachments = [x for x in data['discussion']['attached_elements'] if x['type'] == 'job']
        instance_attachments = [x for x in data['discussion']['attached_elements'] if x['type'] == 'instance']
        self.assertEqual(len(job_attachments), 0)
        self.assertEqual(len(instance_attachments), 0)

    def test_update_discussion_core(self):
        # Create mock discussion
        discussion = data_mocking.create_discussion({
            'title': 'test',
            'description': 'test',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)
        member = self.member

        new_content = 'new content.'
        result, log = discussion_update.update_discussion_core(
            session = self.session,
            discussion = discussion,
            description = new_content,
            member = member,
            log = regular_log.default(),
        )
        print('log', log)
        self.assertTrue(len(log['error'].keys()) == 0)
        self.assertIsNotNone(result)
        self.assertEqual(result['description'], new_content)
