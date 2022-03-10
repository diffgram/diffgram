from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.annotation import instance_template_update


class TeseInstanceTemplateUpdate(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseInstanceTemplateUpdate, self).setUp()
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

    def test_update_instance_template_api(self):
        template_data = {
            'name': 'test template1',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }
        instance_template1 = data_mocking.create_instance_template(template_data, self.session)
        request_data = {
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ],
            'name': 'my instance template',
            'status': 'archived'
        }

        endpoint = "/api/v1/project/{}/instance-template/{}".format(self.project.project_string_id,
                                                                           instance_template1.id)
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
        self.assertEqual(data['instance_template']['instance_list'][0]['nodes'][1]['x'], 5)
        self.assertEqual(data['instance_template']['instance_list'][0]['nodes'][0]['x'], 0)
        self.assertEqual(data['instance_template']['instance_list'][0]['nodes'][0]['y'], 0)
        self.assertEqual(data['instance_template']['instance_list'][0]['nodes'][1]['y'], 5)
        self.assertEqual(data['instance_template']['name'], request_data['name'])

        self.assertTrue('id' in data['instance_template'])
        self.assertEqual(len(data['instance_template']['instance_list']), 1)
        self.assertEqual(data['instance_template']['id'], instance_template1.id)
        self.assertEqual(data['instance_template']['status'], 'archived')

    def test_update_instance_template_core(self):
        template_data = {
            'name': 'test template1',
            'project_id': self.project.id,
            'instance_list': [
                {
                    'type': 'keypoints',
                    'nodes': [{'x': 0, 'y': 0, 'id': 'abc'}, {'x': 5, 'y': 5, 'id': 'cde'}],
                    'edges': [{'from': 'abc', 'to': 'cde'}]
                }
            ]
        }
        instance_template1 = data_mocking.create_instance_template(template_data, self.session)
        name = 'updated instance template'
        new_instance_list = [x.serialize() for x in instance_template1.get_instance_list(self.session)]
        new_instance_list[0]['nodes'][0]['x'] = 2
        new_instance_list[0]['nodes'][0]['y'] = 2
        member = self.session.query(Member).filter(
            Member.id == self.project_data['users'][0].member_id
        ).first()
        result, log = instance_template_update.update_instance_template_core(self.session,
                                                                            member,
                                                                            self.project,
                                                                            name = name,
                                                                            status = 'archived',
                                                                            instance_list = new_instance_list,
                                                                            instance_template_id = instance_template1.id,
                                                                            log = regular_log.default())
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertTrue('instance_list' in result)
        self.assertTrue('name' in result)
        self.assertTrue('id' in result)
        self.assertEqual(len(result['instance_list']), 1)
        self.assertEqual(name, result['name'])
        self.assertEqual('archived', result['status'])
        self.assertEqual(result['instance_list'][0]['nodes'][0]['x'], 2)
        self.assertEqual(result['instance_list'][0]['nodes'][0]['y'], 2)
