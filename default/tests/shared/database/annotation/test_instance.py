from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.annotation.instance import Instance


class TestInstance(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestInstance, self).setUp()
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
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member

    def test_get_child_instance_history(self):
        root = data_mocking.create_instance({'previous_id': None}, self.session)
        instance1 = data_mocking.create_instance({'root_id': root.id}, self.session)
        instance2 = data_mocking.create_instance({'root_id': root.id}, self.session)
        instance3 = data_mocking.create_instance({'root_id': root.id}, self.session)
        instance4 = data_mocking.create_instance({'root_id': 0}, self.session)

        history = Instance.get_child_instance_history(self.session, root.id)

        self.assertEqual(len(history), 4)
        self.assertTrue(instance1 in history)
        self.assertTrue(instance2 in history)
        self.assertTrue(instance3 in history)
        self.assertTrue(root in history)

        self.assertTrue(instance4 not in history)
