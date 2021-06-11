from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model_run import ModelRun
from shared.database.model.model import Model
from base64 import b64encode
from methods.model.model_run_list import model_run_list_core


class TestModelRunList(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestModelRunList, self).setUp()
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

    def test_model_run_list_web(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
        model_run = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run',
            project_id = self.project.id,
            member_created_id = self.member.id,
            model_id = model.id,
            add_to_session = True,
            flush_session = True
        )
        model_run2 = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run',
            project_id = self.project.id,
            member_created_id = self.member.id,
            model_id = model.id,
            add_to_session = True,
            flush_session = True
        )
        request_data = {

        }

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode("{}:{}".format(auth_api.client_id, auth_api.client_secret).encode()).decode('utf-8')

        endpoint = "/api/v1/project/{}/model-runs/list".format(self.project.project_string_id)
        response = self.client.post(
            endpoint,
            data = json.dumps(request_data),
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': 'Basic {}'.format(credentials)
            }
        )
        data = response.json
        self.assertIsNotNone(data.get('model_run_list'))
        self.assertEqual(len(data.get('model_run_list')), 2)
        self.assertIsNotNone(data.get('model_run_list')[0].get('id'))
        self.assertIsNotNone(data.get('model_run_list')[0].get('created_time'))
        self.assertIsNotNone(data.get('model_run_list')[0].get('model_id'))
        self.assertIsNotNone(data.get('model_run_list')[0].get('member_created_id'))
        self.assertIsNotNone(data.get('model_run_list')[0].get('project_id'))
        ids = [m['id'] for m in data.get('model_run_list')]
        for m in [model_run, model_run2]:
            self.assertTrue(m.id in ids)

    def test_model_run_list_core(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
        model_run = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run',
            project_id = self.project.id,
            member_created_id = self.member.id,
            model_id = model.id,
            add_to_session = True,
            flush_session = True
        )
        model_run2 = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run',
            project_id = self.project.id,
            member_created_id = self.member.id,
            model_id = model.id,
            add_to_session = True,
            flush_session = True
        )
        result, log = model_run_list_core(
            session = self.session,
            log = regular_log.default(),
            project_id = self.project.id
        )

        self.assertIsNot(result, False)
        self.assertEqual(len(result), 2)
        self.assertIsNotNone(result[0].get('id'))
        self.assertIsNotNone(result[0].get('model_id'))
        self.assertIsNotNone(result[0].get('member_created_id'))
        self.assertIsNotNone(result[0].get('project_id'))
        self.assertIsNotNone(result[0].get('created_time'))
        ids = [m['id'] for m in result]
        for m in [model_run, model_run2]:
            self.assertTrue(m.id in ids)


