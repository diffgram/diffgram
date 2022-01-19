from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.annotation.instance import Instance
from shared.database.annotation.instance_relation import InstanceRelation


class TestInstanceRelation(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestInstanceRelation, self).setUp()
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

    def test_serialize(self):
        instance1 = data_mocking.create_instance({'root_id': None}, self.session)
        instance2 = data_mocking.create_instance({'root_id': None}, self.session)
        relation = data_mocking.create_instance_relation(
            {'from_instance_id': instance1.id, 'to_instance_id': instance2.id}, self.session)

        result = relation.serialize()

        self.assertEqual(result['id'], relation.id)
        self.assertEqual(result['from_instance_id'], instance1.id)
        self.assertEqual(result['to_instance_id'], instance2.id)

    def test_new(self):
        instance1 = data_mocking.create_instance({'root_id': None}, self.session)
        instance2 = data_mocking.create_instance({'root_id': None}, self.session)
        rel = InstanceRelation.new(
            session = self.session,
            from_instance_id = instance1.id,
            to_instance_id = instance2.id,
            member_created_id = self.member.id,
            member_updated_id = self.member.id
        )

        self.assertEqual(rel.from_instance_id, instance1.id)
        self.assertEqual(rel.to_instance_id, instance2.id)
        self.assertEqual(rel.member_created_id, self.member.id)
        self.assertEqual(rel.member_updated_id, self.member.id)

    def test_get_by_id(self):
        instance1 = data_mocking.create_instance({'root_id': None}, self.session)
        instance2 = data_mocking.create_instance({'root_id': None}, self.session)
        relation = data_mocking.create_instance_relation(
            {'from_instance_id': instance1.id, 'to_instance_id': instance2.id}, self.session)

        relation2 = InstanceRelation.get_by_id(self.session, relation.id)

        self.assertEqual(relation.id, relation2.id)
