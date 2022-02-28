from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from methods.annotation import instance_history


class TestInstanceHistory(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestInstanceHistory, self).setUp()
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

    def test_instance_history_api(self):
        request_data = {}
        root = data_mocking.create_instance({'previous_id': None, 'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance2 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance3 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance4 = data_mocking.create_instance({'root_id': 0}, self.session)

        auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')

        endpoint = f"/api/v1/project/{self.project.project_string_id}/instance/{instance1.id}/history"
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
        self.assertEqual(len(data.get('instance_history')), 4)
        self.assertEqual(data.get('instance_history')[-1]['id'], root.id)   # careful, order dependent
        history_ids = [x['id'] for x in data['instance_history']]
        self.assertTrue(instance1.id in history_ids)
        self.assertTrue(instance2.id in history_ids)
        self.assertTrue(instance3.id in history_ids)

    def test_instance_history_core(self):
        root = data_mocking.create_instance({'previous_id': None, 'project_id': self.project.id}, self.session)
        instance1 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance2 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance3 = data_mocking.create_instance({'root_id': root.id, 'project_id': self.project.id}, self.session)
        instance4 = data_mocking.create_instance({'root_id': 0}, self.session)

        history_serialized, log = instance_history.instance_history_core(
            project = self.project,
            session = self.session,
            instance_id = None
        )
        self.assertFalse(history_serialized)
        self.assertIsNotNone(log.get('error'))
        self.assertIsNotNone(log.get('error').get('root_id'))

        history_serialized, log = instance_history.instance_history_core(
            session = self.session,
            project = self.project,
            instance_id = instance1.id
        )

        self.assertEqual(len(history_serialized), 4)
        ids = [x['id'] for x in history_serialized]
        self.assertTrue(instance1.id in ids)
        self.assertTrue(instance2.id in ids)
        self.assertTrue(instance3.id in ids)
