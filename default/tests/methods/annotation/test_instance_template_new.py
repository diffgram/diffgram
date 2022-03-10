from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.annotation import instance_template_new


class TeseInstanceTemplateNew(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseInstanceTemplateNew, self).setUp()
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

    def test_new_instance_template_api(self):
        request_data = {
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ],
            'name': 'my instance template',
            'reference_width': 600,
            'reference_height': 800
        }

        endpoint = f"/api/v1/project/{self.project.project_string_id}/instance-template/new"
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
        self.assertTrue('instance_template' in data)
        self.assertTrue('instance_list' in data['instance_template'])
        self.assertTrue('name' in data['instance_template'])
        self.assertTrue('id' in data['instance_template'])
        self.assertTrue('reference_width' in data['instance_template'])
        self.assertTrue('reference_height' in data['instance_template'])
        self.assertEqual(data['instance_template']['reference_height'], 800)
        self.assertEqual(data['instance_template']['reference_width'], 600)
        self.assertEqual(len(data['instance_template']['instance_list']), 1)

    def test_new_instance_template_core(self):
        instance_list = [
            {
                'type': 'keypoints',
                'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                'edges': [{'from': 'abc', 'to': 'cde'}]
            }
        ]
        reference_height = 800
        reference_width = 600
        name = 'test instance template'
        member = self.session.query(Member).filter(
            Member.id == self.project_data['users'][0].member_id
        ).first()
        result, log = instance_template_new.new_instance_template_core(self.session,
                                                                       member,
                                                                       name,
                                                                       self.project,
                                                                       instance_list,
                                                                       reference_height,
                                                                       reference_width,
                                                                       log = regular_log.default())
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertTrue('instance_list' in result)
        self.assertTrue('name' in result)
        self.assertTrue('id' in result)
        self.assertEqual(len(result['instance_list']), 1)
        self.assertEqual(result['reference_height'], reference_height)
        self.assertEqual(result['reference_width'], reference_width)
