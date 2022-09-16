from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from enum import Enum


class TestPermissionsChecker(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestPermissionsChecker, self).setUp()
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     'no_roles': True
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.editor_role = Role.new(
            session = self.session,
            name = 'editor_test',
            permissions_list = ['view_data', 'list_data', 'edit_data'],
            project_id = self.project.id
        )
        self.view_role = Role.new(
            session = self.session,
            name = 'viewer_test',
            permissions_list = ['view_data', 'list_data'],
            project_id = self.project.id,
        )
        self.policy_engine = PolicyEngine(session = self.session, project = self.project)

    def test_member_has_any_project_role(self):
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.project,
            object_id = self.project.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )

        result: PermissionResult = self.policy_engine.member_has_any_project_role(
            member = self.member,
            roles = ['viewer_test'],
            project_id = self.project.id,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.member_id, self.member.id)
        self.assertEqual(result.object_type, ValidObjectTypes.project.name)
        self.assertEqual(result.object_id, self.project.id)

        result = self.policy_engine.member_has_any_project_role(
            member = self.member,
            roles = ['editor_test'],
            project_id = self.project.id
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.member_id, self.member.id)
        self.assertEqual(result.object_type, ValidObjectTypes.project.name)
        self.assertEqual(result.object_id, self.project.id)

        result = self.policy_engine.member_has_any_project_role(
            member = self.member,
            roles = ['editor_test', 'blablab', 'viewer_test'],
            project_id = self.project.id
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.member_id, self.member.id)
        self.assertEqual(result.object_type, ValidObjectTypes.project.name)
        self.assertEqual(result.object_id, self.project.id)

    def test_get_allowed_object_id_list(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': 'myproject',
            'no_roles': True
        }, self.session)
        member2 = data_mocking.register_member(user, session = self.session)
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [],
            'access_type': 'restricted'
        }, self.session)
        ds2 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [],
            'access_type': 'restricted'
        }, self.session)
        ds3 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [],
            'access_type': 'restricted'
        }, self.session)
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds1.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds2.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds3.id,
            role_id = self.editor_role.id,
            member_id = member2.id
        )

        class TestEnum(Enum):
            unexisting_perm = 'some_perm'

        result = self.policy_engine.get_allowed_object_id_list(
            member = self.member,
            object_type = ValidObjectTypes.dataset,
            perm = TestEnum.unexisting_perm,
        )
        self.assertFalse(result.allow_all)
        self.assertTrue(ds1.id not in result.allowed_object_id_list)
        self.assertTrue(ds2.id not in result.allowed_object_id_list)
        self.assertTrue(ds3.id not in result.allowed_object_id_list)
