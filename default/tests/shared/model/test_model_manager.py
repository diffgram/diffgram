# Import necessary modules and classes
from methods.regular.regular_api import *  # Regular API methods
from default.tests.test_utils import testing_setup  # Test setup for DiffgramBaseTestCase
from shared.tests.test_utils import common_actions, data_mocking  # Test utilities for common actions and data mocking
from shared.database.model.model import Model  # Database model for Model
from shared.model.model_manager import ModelManager  # Model manager class

class TestModelManager(testing_setup.DiffgramBaseTestCase):
    """
    Test cases for the ModelManager class
    """

    def setUp(self):
        """
        Set up the test environment
        """
        super(TestModelManager, self).setUp()

        # Create a new project with a user for testing
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

    def test_check_instances_and_create_new_models(self):
        """
        Test the check_instances_and_create_new_models method
        """

        # Create a ModelManager instance with a list of model instances
        model_manager = ModelManager(
            session = self.session,
            instance_list_dicts = [
                {
                    'model_ref': 'mymodel1',
                    'model_run_ref': 'mymodel_run1',
                },
                {
                    'model_ref': 'mymodel2',
                    'model_run_ref': 'mymodel_run2',
                },
                {
                    'model_ref': 'mymodel3',
                    'model_run_ref': 'mymodel_run3',
                }
            ],
            project = self.project,
            member = self.member
        )

        # Call the method to check instances and create new models
        created_models, created_runs = model_manager.check_instances_and_create_new_models(use_reference_ids = True)

        # Assert that 3 new models have been created
        self.assertEqual(len(created_models), 3)

        # Check the reference_ids of the created models
        refs = [m.reference_id for m in created_models]
        self.assertTrue('mymodel1' in refs)
        self.assertTrue('mymodel2' in refs)
        self.assertTrue('mymodel3' in refs)

        # Check the reference_ids of the created model runs
        refs_runs = [m.reference_id for m in created_runs]
        self.assertTrue('mymodel_run1' in refs_runs)
        self.assertTrue('mymodel_run2' in refs_runs)
        self.assertTrue('mymodel_run3' in refs_runs)
