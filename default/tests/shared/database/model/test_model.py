from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model import Model


class TestModel(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestModel, self).setUp()
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

    def test_new(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )

        self.assertEqual(model.reference_id, 'test_model')
        self.assertEqual(model.project_id, self.project.id)
        self.assertEqual(model.member_created_id, self.member.id)

    def test_get_by_id(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model2',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )

        model2 = Model.get_by_id(self.session, model.id)
        self.assertEqual(model.id, model2.id)
        self.assertEqual(model.reference_id, model2.reference_id)

    def test_get_by_reference(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model3',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )

        model2 = Model.get_by_reference_id(self.session, model.reference_id, project_id = self.project.id)
        self.assertEqual(model.id, model2.id)
        self.assertEqual(model.reference_id, model2.reference_id)

    def test_list(self):
        model1 = Model.new(
            session = self.session,
            reference_id = 'test_model__1',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
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
        )

        id_list = [m.id for m in models]

        self.assertTrue(model1.id in id_list)
        self.assertTrue(model2.id in id_list)
        self.assertTrue(model3.id in id_list)
