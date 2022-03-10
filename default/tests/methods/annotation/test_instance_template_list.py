from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.annotation import instance_template_list


class TeseInstanceTemplateList(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseInstanceTemplateList, self).setUp()
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

    def test_list_instance_template_api(self):
        request_data = {}
        instance_template1 = data_mocking.create_instance_template({
            'name': 'test template1',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }, self.session)
        instance_template2 = data_mocking.create_instance_template({
            'name': 'test template2',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }, self.session)
        instance_template3 = data_mocking.create_instance_template({
            'name': 'test template3',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }, self.session)
        endpoint = f"/api/v1/project/{self.project.project_string_id}/instance-template/list"
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
        self.assertTrue('instance_template_list' in data)
        self.assertEqual(len(data['instance_template_list']), 3)

    def test_list_instance_template_core(self):
        instance_template = data_mocking.create_instance_template({
            'name': 'test template',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }, self.session)
        member = self.session.query(Member).filter(
            Member.id == self.project_data['users'][0].member_id
        ).first()
        result, log = instance_template_list.list_instance_templates_core(self.session,
                                                                          self.project,
                                                                          log = regular_log.default())
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(len(result), 1)
