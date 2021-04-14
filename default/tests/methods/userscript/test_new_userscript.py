from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member

from shared.database.userscript.userscript import UserScript
#from default.methods.userscript.userscript import __userscript_new


class TestUserScript(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestUserScript, self).setUp()
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


    def test_new_userscript_database(self):

        external_src_list = ['test', '2']
        userscript = data_mocking.create_userscript(
            {'project': self.project,
             'name': 'test',
             'code': 'test',
             'external_src_list': external_src_list
             }, self.session)
        self.assertIsNotNone(userscript.id)


    def test_new_userscript_api(self):

        external_src_list = ['test', '2']
        example = {
             'name': 'test',
             'code': 'test',
             'external_src_list': external_src_list
            }

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')

        endpoint = "/api/v1/project/{}/userscript/new".format(self.project.project_string_id)
        
        response = self.client.post(
            endpoint,
            data = json.dumps(example),
            headers = {
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)

        self.assertTrue('userscript' in data)

        userscript = response.json.get('userscript')

        self.assertFalse(userscript.get('is_public'))

        self.assertIsNotNone(userscript.get('id'))
        self.assertIsNotNone(userscript.get('name'))
        self.assertIsNotNone(userscript.get('project_id'))
        self.assertIsNotNone(userscript.get('time_created'))

        self.assertEqual(len(userscript.get('external_src_list')), len(external_src_list))


# getting strange import error here not sure why
"""
    def test_new_userscript_core(self):

        external_src_list = ['test', '2']
        input = {
             'name': 'test',
             'code': 'test',
             'external_src_list': external_src_list
            }

        userscript = __userscript_new(
            project_string_id = self.project.project_string_id,
            session = self.session,
            input = input
        )
        self.assertIsNotNone(userscript.id)
"""