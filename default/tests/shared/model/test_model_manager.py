from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model import Model
from shared.model.model_manager import ModelManager


class TestModelManager(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestModelManager, self).setUp()
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

        created_models, created_runs = model_manager.check_instances_and_create_new_models(use_reference_ids = True)

        self.assertEqual(len(created_models), 3)
        refs = [m.reference_id for m in created_models]
        refs_runs = [m.reference_id for m in created_runs]
        self.assertTrue('mymodel1' in refs)
        self.assertTrue('mymodel2' in refs)
        self.assertTrue('mymodel3' in refs)
        self.assertTrue('mymodel_run1' in refs_runs)
        self.assertTrue('mymodel_run2' in refs_runs)
        self.assertTrue('mymodel_run3' in refs_runs)
