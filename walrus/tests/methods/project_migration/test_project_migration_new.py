from methods.regular.regular_api import *
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.project_migration import project_migration_new
from unittest.mock import patch

class TestProjectMigrationNew(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestProjectMigrationNew, self).setUp()
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
        self.auth_api = common_actions.create_project_auth(project = self.project,
                                                           session = self.session,
                                                           role = "admin")
        self.member = self.auth_api.member

    def test_api_new_project_migration(self):
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session, role = "admin")
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        conn = data_mocking.create_connection({'name': 'test', 'integration_name': 'labelbox', 'project_id': self.project.id}, self.session)
        with patch.object(project_migration_new, 'initialize_migration_threaded') as mock:
            with self.client.session_transaction() as session:
                endpoint = f"/api/walrus/project/{self.project.project_string_id}/project-migration/new"
            response = self.client.post(
                endpoint,
                data = json.dumps(
                    {
                        'labelbox_project_id': 'test123',
                        'connection_id': conn.id,
                        'import_schema': True,
                        'import_files': True,                  
                    }
                ),
                headers = {
                    'directory_id': str(self.project.directory_default_id),
                    'Authorization': f"Basic {credentials}"
                }
            )
            data = response.json
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(data['id'])
            self.assertEqual(data['connection_id'], conn.id)
            self.assertEqual(data['import_schema'], True)
            self.assertEqual(data['import_files'], True)

    def test_new_project_migration_core(self):
        conn = data_mocking.create_connection(
            {'name': 'test', 'integration_name': 'labelbox', 'project_id': self.project.id}, self.session)
        with patch.object(project_migration_new, 'initialize_migration_threaded') as mock:
            data, log = project_migration_new.new_project_migration_core(
                session = self.session,
                labelbox_project_id = 'test123',
                project_string_id = self.project.project_string_id,
                connection_id = conn.id,
                import_schema = True,
                import_files = True,
                existing_migration_id = None,
                member = self.member,
                log = regular_log.default()
            )
            mock.assert_called_once()
            self.assertEqual(len(log['error'].keys()), 0)
            self.assertIsNotNone(data['id'])
            self.assertEqual(data['connection_id'], conn.id)
            self.assertEqual(data['import_schema'], True)
            self.assertEqual(data['import_files'], True)
