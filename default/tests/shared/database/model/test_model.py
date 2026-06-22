from methods.regular.regular_api import *  # Import necessary methods from the regular_api module
from default.tests.test_utils import testing_setup  # Import testing setup module
from shared.tests.test_utils import common_actions, data_mocking  # Import common actions and data mocking modules
from shared.database.model.model import Model  # Import Model class

class TestModel(testing_setup.DiffgramBaseTestCase):
    """
    Test class for the Model class in the shared.database.model.model module.
    Inherits from DiffgramBaseTestCase, providing test case infrastructure.
    """

    def setUp(self):
        """
        Set up the test environment.
        This method is called before each test method is executed.
        """
        super(TestModel, self).setUp()  # Call the parent class's setUp method

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
        )  # Create a new project with a user for testing

        self.project = project_data['project']  # Assign the created project to the project variable
        self.project_data = project_data  # Assign the project data to the project_data variable
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)  # Create project authentication
        self.member = self.auth_api.member  # Assign the member to the member variable

    def test_new(self):
        """
        Test creating new Model instances.
        """
        model = Model.new(
            session = self.session,
            reference_id = 'test_model',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )  # Create a new Model instance

        self.assertEqual(model.reference_id, 'test_model')  # Assert that the reference_id is 'test_model'
        self.assertEqual(model.project_id, self.project.id)  # Assert that the project_id is the project's id
        self.assertEqual(model.member_created_id, self.member.id)  # Assert that the member_created_id is the member's id

    def test_get_by_id(self):
        """
        Test getting a Model instance by its id.
        """
        model = Model.new(
            session = self.session,
            reference_id = 'test_model2',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )  # Create a new Model instance for testing

        model2 = Model.get_by_id(self.session, model.id)  # Get the Model instance by its id

        self.assertEqual(model.id, model2.id)  # Assert that the ids are the same
        self.assertEqual(model.reference_id, model2.reference_id)  # Assert that the reference_ids are the same

    def test_get_by_reference(self):
        """
        Test getting a Model instance by its reference_id.
        """
        model = Model.new(
            session = self.session,
            reference_id = 'test_model3',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )  # Create a new Model instance for testing

        model2 = Model.get_by_reference_id(self.session, model.reference_id, project_id = self.project.id)  # Get the Model instance by its reference_id

        self.assertEqual(model.id, model2.id)  # Assert that the ids are the same
        self.assertEqual(model.reference_id, model2.reference_id)  # Assert that the reference_ids are the same

    def test_list(self):
        """
        Test listing Model instances.
        """
        model1 = Model.new(
            session = self.session,
            reference_id = 'test_model__1',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )  # Create new Model instances for testing
        model2 = Model.new(
            session = self.session,
            reference_id = 'test_model__2',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )

        model3 = Model.new(
            session = self.session,
            reference_id = 'test_model__3',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )

        models = Model.list(
            session = self.session,
            project_id = self.project.id
        )  # List Model instances

        id_list = [m.id for m in models]  # Create a list of Model instance ids

        self.assertTrue(model1.id in id_list)  # Assert that the id is in the list
        self.assertTrue(model2.id in id_list)  # Assert that the id is in the list
        self.assertTrue(model3.id in id_list)  # Assert that the id is in the list
