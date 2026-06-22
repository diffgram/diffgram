from methods.regular.regular_api import RegularApi  # Renamed to follow Python naming conventions
from default.tests.test_utils import TestingSetup  # Renamed to follow Python naming conventions
from shared.tests.test_utils import CommonActions, DataMocking
from shared.database.annotation.instance import Instance


class TestInstance(TestingSetup):
    """
    Test cases for the Instance model.
    """

    def setUp(self):
        super().setUp()
        project_data = DataMocking.create_project_with_context(
            {
                'users': [
                    {
                        'username': 'Test',
                        'email': 'test@test.com',
                        'password': 'diffgram123',
                    }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.auth_api = CommonActions.create_project_auth(project=self.project, session=self.session)
        self.member = self.auth_api.member

    def tearDown_method(self, method):
        """
        Clean up the database after each test.
        """
        super().tearDown_method(method)
        root = Instance.get_root_instance(self.session, self.project.id)
        if root:
            Instance.delete_instance_and_children(self.session, root.id)

    def test_get_child_instance_history(self):
        """
        Test the get_child_instance_history method.
        """
        root = DataMocking.create_instance({'previous_id': None}, self.session)
        instance1 = DataMocking.create_instance({'root_id': root.id}, self.session)
        instance2 = DataMocking.create_instance({'root_id': root.id}, self.session)
        instance3 = DataMocking.create_instance({'root_id': root.id}, self.session)
        instance4 = DataMocking.create_instance({'root_id': 0}, self.session)

        history = Instance.get_child_instance_history(self.session, root.id)

        self.assertEqual(len(history), 4 + 1)  # Added a check for the expected length of the history
        self.assertTrue(instance1 in history)
        self.assertTrue(instance2 in history)
        self.assertTrue(instance3 in history)
        self.assertTrue(root in history)  # Added a check for the root instance in the history
        self.assertTrue(instance4 not in history)
