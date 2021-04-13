from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.annotation.instance_template import InstanceTemplate


class TestInstanceTemplate(testing_setup.DiffgramBaseTestCase):
    """
        
        
        
    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestInstanceTemplate, self).setUp()
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
        instance_template = InstanceTemplate.new(
            session = self.session,
            project = self.project,
            member_created = self.member,
            name = 'instance template test',
            instance_list = []
        )

        query = self.session.query(InstanceTemplate).filter(InstanceTemplate.id == instance_template.id).first()
        self.assertIsNotNone(query)
        self.assertEqual(instance_template.id, query.id)

    def test_serialize(self):
        instance_template1 = InstanceTemplate.new(
            session = self.session,
            project = self.project,
            member_created = self.member,
            name = 'instance template 1',
            instance_list = []
        )

        result = instance_template1.serialize(self.session)

        self.assertTrue('id' in result)
        self.assertEqual(result['id'], instance_template1.id)
        self.assertTrue('name' in result)
        self.assertEqual(result['name'], instance_template1.name)
        self.assertTrue('project_id' in result)
        self.assertEqual(result['project_id'], instance_template1.project_id)
        self.assertTrue('member_created_id' in result)
        self.assertEqual(result['member_created_id'], instance_template1.member_created_id)
        self.assertTrue('created_time' in result)
        self.assertEqual(result['created_time'], instance_template1.created_time)
        self.assertTrue('deleted_time' in result)
        self.assertEqual(result['deleted_time'], instance_template1.deleted_time)

    def test_list(self):
        instance_template1 = InstanceTemplate.new(
            session = self.session,
            project = self.project,
            member_created = self.member,
            name = 'instance template 1',
            instance_list = []
        )

        instance_template2 = InstanceTemplate.new(
            session = self.session,
            project = self.project,
            member_created = self.member,
            name = 'instance template 1',
            instance_list = []
        )
        instance_template_list = InstanceTemplate.list(
            session = self.session,
            project = self.project,
        )

        self.assertTrue(instance_template1 in instance_template_list)
        self.assertTrue(instance_template2 in instance_template_list)
        self.assertEqual(len(instance_template_list), 2)
