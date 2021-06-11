from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model_run import ModelRun
from shared.database.model.model import Model


class TestModelRun(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestModelRun, self).setUp()
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
        model_run = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run',
            project_id = self.project.id,
            member_created_id = self.member.id,
            model_id = model.id,
            add_to_session = True,
            flush_session = True
        )

        self.assertEqual(model_run.reference_id, 'test_model_run')
        self.assertEqual(model_run.project_id, self.project.id)
        self.assertEqual(model_run.member_created_id, self.member.id)

    def test_get_by_id(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model_2',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
        model_run = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run_2',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            model_id = model.id,
            flush_session = True
        )

        model_run2 = ModelRun.get_by_id(self.session, model_run.id)
        self.assertEqual(model_run.id, model_run2.id)
        self.assertEqual(model_run.reference_id, model_run2.reference_id)

    def test_get_by_reference(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model_3',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
        model_run = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run_3',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            model_id = model.id,
            flush_session = True
        )

        model_run2 = ModelRun.get_by_reference_id(self.session, model_run.reference_id, model_id = model.id)
        self.assertEqual(model_run.id, model_run2.id)
        self.assertEqual(model_run.reference_id, model_run2.reference_id)

    def test_list(self):
        model = Model.new(
            session = self.session,
            reference_id = 'test_model_4',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            flush_session = True
        )
        model_run1 = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run_4',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            model_id = model.id,
            flush_session = True
        )
        model_run2 = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run_5',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            model_id = model.id,
            flush_session = True
        )

        model_run3 = ModelRun.new(
            session = self.session,
            reference_id = 'test_model_run_6',
            project_id = self.project.id,
            member_created_id = self.member.id,
            add_to_session = True,
            model_id = model.id,
            flush_session = True
        )

        models = ModelRun.list(
            session = self.session,
            project_id = self.project.id,
            model_id = model.id
        )

        id_list = [m.id for m in models]

        self.assertTrue(model_run1.id in id_list)
        self.assertTrue(model_run2.id in id_list)
        self.assertTrue(model_run3.id in id_list)
