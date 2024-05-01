from methods.regular.regular_api import ModelRun as RegularModelRun, Model as RegularModel
from default.tests.test_utils import TestBase
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model_run import ModelRun
from shared.database.model.model import Model

class TestModelRun(TestBase):
    """
    Test cases for ModelRun model.
    """

    def setUp(self):
        super().setUp()
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
        self.auth_api = common_actions.create_project_auth(project=self.project, session=self.session)
        self.member = self.auth_api.member

    def tearDown(self):
        """
        Clean up the project created in the setUp method.
        """
        self.session.delete(self.project)
        self.session.commit()

    def create_model(self):
        model = Model.new(
            session=self.session,
            reference_id='test_model',
            project_id=self.project.id,
            member_created_id=self.member.id,
            add_to_session=True,
            flush_session=True
        )
        return model

    def create_model_run(self, model):
        model_run = ModelRun.new(
            session=self.session,
            reference_id='test_model_run',
            project_id=self.project.id,
            member_created_id=self.member.id,
            model_id=model.id,
            add_to_session=True,
            flush_session=True
        )
        return model_run

    def test_new(self):
        model = self.create_model()
        model_run = self.create_model_run(model)

        self.assertEqual(model_run.reference_id, 'test_model_run')
        self.assertEqual(model_run.project_id, self.project.id)
        self.assertEqual(model_run.member_created_id, self.member.id)

    def test_get_by_id(self):
        model = self.create_model()
        model_run = self.create_model_run(model)

        model_run2 = ModelRun.get_by_id(self.session, model_run.id)
        self.assertEqual(model_run.id, model_run2.id)
        self.assertEqual(model_run.reference_id, model_run2.reference_id)

    def test_get_by_reference(self):
        model = self.create_model()
        model_run = self.create_model_run(model)

        model_run2 = ModelRun.get_by_reference_id(self.session, model_run.reference_id, model_id=model.id)
        self.assertEqual(model_run.id, model_run2.id)
        self.assertEqual(model_run.reference_id, model_run2.reference_id)

    def test_list(self):
        model = self.create_model()
        model_run1 = self.create_model_run(model)
        model_run2 = self.create_model_run(model)
        model_run3 = self.create_model_run(model)

        models = ModelRun.list(
            session=self.session,
            project_id=self.project.id,
            model_id=model.id
        )

        id_list = [m.id for m in models]

        self.assertTrue(model_run1.id in id_list)
        self.assertTrue(model_run2.id in id_list)
        self.assertTrue(model_run3.id in id_list)
