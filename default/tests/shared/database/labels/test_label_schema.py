from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.labels.label_schema import LabelSchema
from unittest.mock import patch


class TestLabelSchema(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestLabelSchema, self).setUp()
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

    def test_new(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )

        self.assertEqual(schema.name, 'test')
        self.assertEqual(schema.project.id, self.project.id)
        self.assertEqual(schema.member_created_id, self.member.id)

    def test_serialize(self):
        data = {
            'name': 'test',
            'project_id': self.project.id,
            'member_created_id': self.member.id
        }
        schema = data_mocking.create_label_schema(data, self.session)

        self.assertEqual(schema.name, data['name'])
        self.assertEqual(schema.project_id, data['project_id'])
        self.assertEqual(schema.member_created_id, data['member_created_id'])
