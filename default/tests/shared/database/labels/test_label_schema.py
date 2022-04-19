from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.labels.label_schema import LabelSchema, LabelSchemaLink
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

    def test_get_by_id(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )

        fetched_schema = LabelSchema.get_by_id(session = self.session, id = schema.id)

        self.assertEqual(fetched_schema.id, schema.id)
        self.assertEqual(fetched_schema.name, schema.name)
        self.assertEqual(fetched_schema.project.id, schema.project.id)


    def test_get_label_files(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        id_list = []
        for i in range(0, 5):
            label1 = data_mocking.create_label({
                'name': f'apple {i}',
            }, self.session)
            label_file1 = data_mocking.create_label_file({
                'label': label1,
                'project_id': self.project.id
            }, self.session)
            schema_link = LabelSchemaLink.new_label_link(
                session = self.session,
                schema_id = schema.id,
                label_file_id = label_file1.id,
                member_created_id = self.member.id
            )
            id_list.append(label_file1.id)
        self.session.commit()
        label_files = schema.get_label_files(session = self.session)
        self.assertEqual(len(label_files), 5)
        for elm in label_files:
            self.assertTrue(elm.id in id_list)

    def test_get_attribute_groups(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        id_list = []
        for i in range(0, 5):
            attr = data_mocking.create_attribute_template_group({
                'name': f'apple {i}',
            }, self.session)
            schema_link = LabelSchemaLink.new_attribute_group_link(
                session = self.session,
                schema_id = schema.id,
                attribute_group_id = attr.id,
                member_created_id = self.member.id
            )
            id_list.append(attr.id)
        self.session.commit()
        attr_list = schema.get_attribute_groups(session = self.session)
        self.assertEqual(len(attr_list), 5)
        for elm in attr_list:
            self.assertTrue(elm.id in id_list)

    def test_get_instance_templates(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        id_list = []
        for i in range(0, 5):
            template = data_mocking.create_instance_template({
                'name': f'apple {i}',
            }, self.session)
            schema_link = LabelSchemaLink.new_instance_template_link(
                session = self.session,
                schema_id = schema.id,
                instance_template_id = template.id,
                member_created_id = self.member.id
            )
            id_list.append(template.id)
        self.session.commit()
        template_list = schema.get_instance_templates(session = self.session)
        self.assertEqual(len(template_list), 5)
        for elm in template_list:
            self.assertTrue(elm.id in id_list)


    def test_serialize(self):
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test2',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project2 = project_data['project']
        schema1 = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema2 = LabelSchema.new(
            session = self.session,
            name = 'test2',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        schema3 = LabelSchema.new(
            session = self.session,
            name = 'test3',
            project_id = self.project.id,
            member_created_id = self.member.id
        )

        schema4 = LabelSchema.new(
            session = self.session,
            name = 'test4',
            project_id = self.project2.id,
            member_created_id = self.member.id
        )
        id_list = [schema1.id, schema2.id, schema3.id]
        results = LabelSchema.list(session = self.session, project_id = self.project.id)
        results2 = LabelSchema.list(session = self.session, project_id = self.project2.id)

        self.assertEqual(len(results), 3)
        self.assertEqual(len(results2), 1)
        for elm in results:
            self.assertTrue(elm.id in id_list)
        for elm in results2:
            self.assertTrue(elm.id in [schema4.id])


class TestLabelSchemaLink(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestLabelSchemaLink, self).setUp()
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

    def test_new_label_link(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        schema_link = LabelSchemaLink.new_label_link(
            session = self.session,
            schema_id = schema.id,
            label_file_id = label_file.id,
            member_created_id = self.member.id
        )

        self.assertEqual(schema_link.schema_id, schema.id)
        self.assertEqual(schema_link.label_file_id, label_file.id)
        self.assertEqual(schema_link.member_created_id, self.member.id)

    def test_new_instance_template_link(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        instance_template = data_mocking.create_instance_template({'name': 'test'}, self.session)
        schema_link = LabelSchemaLink.new_instance_template_link(
            session = self.session,
            schema_id = schema.id,
            instance_template_id = instance_template.id,
            member_created_id = self.member.id
        )

        self.assertEqual(schema_link.schema_id, schema.id)
        self.assertEqual(schema_link.instance_template_id, instance_template.id)
        self.assertEqual(schema_link.member_created_id, self.member.id)

    def test_serialize(self):
        schema = LabelSchema.new(
            session = self.session,
            name = 'test',
            project_id = self.project.id,
            member_created_id = self.member.id
        )
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        schema_link = LabelSchemaLink.new_label_link(
            session = self.session,
            schema_id = schema.id,
            label_file_id = label_file.id,
            member_created_id = self.member.id
        )

        data = schema_link.serialize()

        self.assertEqual(data['schema_id'], schema.id)
        self.assertEqual(data['label_file_id'], label_file.id)
        self.assertEqual(data['member_created_id'], self.member.id)
