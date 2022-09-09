from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from shared.database.source_control.file_perms import FilePermissions, FileRolesPermissions, FileDefaultRoles
from shared.database.source_control.dataset_perms import DatasetPermissions, DatasetDefaultRoles, DatasetRolesPermissions
from shared.database.project_perms import ProjectDefaultRoles, ProjectPermissions
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
                     'project_roles': ['admin'],
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project, session = self.session)
        self.member = self.auth_api.member
        self.policy_engine = PolicyEngine(session = self.session, project = self.project)

    def test_has_perm__direct_perm(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'no_roles': True,
            'member_id': self.member.id
        }, self.session)
        member2 = user.member
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

        ## Assign Permissions
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.file,
            object_id = file.id,
            member_id = member2.id,
            default_role_name = FileDefaultRoles.file_viewer
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_delete,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)
        # Now Assign Admin Permissions
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.file,
            object_id = file.id,
            member_id = member2.id,
            default_role_name = FileDefaultRoles.file_admin
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_delete,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)

    def test_has_perm__project_perm(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'no_roles': True,
            'member_id': self.member.id
        }, self.session)
        member2 = user.member
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

        # Assign Permissions
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.project,
            object_id = self.project.id,
            member_id = member2.id,
            default_role_name = ProjectDefaultRoles.editor
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        # Now test with project viewer role
        user = data_mocking.register_user({
            'username': 'test2_user',
            'email': 'test2@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'no_roles': True,
            'member_id': self.member.id
        }, self.session)
        member2 = user.member
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.project,
            object_id = self.project.id,
            member_id = member2.id,
            default_role_name = ProjectDefaultRoles.viewer
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

    def test_has_perm__dataset_perm(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'no_roles': True,
            'member_id': self.member.id
        }, self.session)
        member2 = user.member
        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [file]
        }, self.session)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

        # Assign Permissions
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds1.id,
            member_id = member2.id,
            default_role_name = DatasetDefaultRoles.dataset_viewer
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_view,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_delete,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

        # Assign role dataset editor
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds1.id,
            member_id = member2.id,
            default_role_name = DatasetDefaultRoles.dataset_editor
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_edit,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_delete,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, False)

        # Assign role dataset admin
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            object_id = ds1.id,
            member_id = member2.id,
            default_role_name = DatasetDefaultRoles.dataset_admin
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = FilePermissions.file_delete,
            object_id = file.id,
            object_type = ValidObjectTypes.file
        )
        self.assertEqual(result_perm.allowed, True)
