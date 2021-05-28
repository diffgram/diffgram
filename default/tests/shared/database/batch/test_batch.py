from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member

from shared.database.batch.batch import InputBatch


class TestBatch(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestBatch, self).setUp()
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
        batch = InputBatch.new(
            session = self.session,
            status = 'test_status',
            project_id = self.project.id,
            member_created_id = self.member.id,
            memeber_updated_id = self.member.id,
            pre_labeled_data = {},
            add_to_session = True,
            flush_session = True
        )

        self.assertEqual(batch.status, 'test_status')
        self.assertEqual(batch.project_id, self.project.id)
        self.assertEqual(batch.member_created_id, self.member.id)
        self.assertEqual(batch.member_updated_id, self.member.id)
        self.assertEqual(batch.pre_labeled_data, {})

    def test_serialize(self):
        batch = InputBatch.new(
            session = self.session,
            status = 'test_status',
            project_id = self.project.id,
            member_created_id = self.member.id,
            memeber_updated_id = self.member.id,
            pre_labeled_data = {},
            add_to_session = True,
            flush_session = True
        )
        data = batch.serialize()
        self.assertEqual(batch.id, data['id'])
        self.assertEqual(batch.project_id, data['project_id'])
        self.assertEqual(batch.member_created_id, data['member_created_id'])
        self.assertEqual(batch.member_updated_id, data['member_updated_id'])
        self.assertEqual(batch.status, data['status'])

    def test_get_by_id(self):
        batch = InputBatch.new(
            session = self.session,
            status = 'test_status',
            project_id = self.project.id,
            member_created_id = self.member.id,
            memeber_updated_id = self.member.id,
            pre_labeled_data = {},
            add_to_session = True,
            flush_session = True
        )
        batch2 = InputBatch.get_by_id(self.session, batch.id)
        self.assertEqual(batch.id, batch2.id)
