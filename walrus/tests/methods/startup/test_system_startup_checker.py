from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.startup.system_startup_checker import WalrusServiceSystemStartupChecker
from unittest.mock import patch


class TestWalrusServiceSystemStartupChecker(testing_setup.DiffgramBaseTestCase):

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestWalrusServiceSystemStartupChecker, self).setUp()
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

    def test_execute_startup_checks(self):
        checker = WalrusServiceSystemStartupChecker()
        with patch.object(checker, 'execute_startup_checks') as mock_1:
            result = checker.execute_startup_checks()
            self.assertTrue(result)
            mock_1.assert_called_once()
