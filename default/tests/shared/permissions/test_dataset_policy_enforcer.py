from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from shared.database.source_control.dataset_perms import DatasetPermissions, DatasetDefaultRoles
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

    def test_has_perm(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'no_roles': True,
            'member_id': self.member.id
        }, self.session)
        member2 = user.member
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = DatasetPermissions.dataset_view,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset
        )
        self.assertEqual(result_perm.allowed, False)
        RoleMemberObject.new(
            session = self.session,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetDefaultRoles.dataset_viewer,
            member_id = member2.id
        )
        self.session.commit()
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = DatasetPermissions.dataset_view,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset
        )
        self.assertEqual(result_perm.allowed, True)

        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = DatasetPermissions.dataset_edit,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset
        )
        self.assertEqual(result_perm.allowed, False)

        # Add Editor Role
        RoleMemberObject.new(
            session = self.session,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetDefaultRoles.dataset_editor,
            member_id = member2.id
        )
        result_perm = self.policy_engine.member_has_perm(
            member = member2,
            perm = DatasetPermissions.dataset_edit,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset
        )
        self.assertEqual(result_perm.allowed, True)

    def test_get_allowed_object_id_list(self):
        project_data2 = data_mocking.create_project_with_context(
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
        self.project2 = project_data2['project']
        self.project_data2 = project_data2
        user = data_mocking.register_user({
            'username': 'test2_user',
            'email': 'test2@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project2.project_string_id,
            'project_roles': ['admin'],
            'member_id': self.member.id
        }, self.session)
        self.policy_engine2 = PolicyEngine(session = self.session, project = self.project2)
        member2 = user.member
        ds1 = data_mocking.create_directory({
            'project': self.project2,
            'user': self.project_data2['users'][0],
            'files': []
        }, self.session)

        restricted_ds = data_mocking.create_directory({
            'project': self.project2,
            'access_type': 'restricted',
            'user': self.project_data2['users'][0],
            'files': []
        }, self.session)

        class TestEnum(Enum):
            unexisting_perm = 'some_perm'

        result = self.policy_engine2.get_allowed_object_id_list(
            member = member2,
            object_type = ValidObjectTypes.dataset,
            perm = DatasetPermissions.dataset_view,
        )
        self.assertTrue(result.allow_all)
        self.assertEqual(result.allowed_object_id_list, [])

        # Test User inherits all perms from project admin role.
        # In this case we can test any perm (even a not existent) and we will get access granted.
        result = self.policy_engine2.get_allowed_object_id_list(
            member = member2,
            object_type = ValidObjectTypes.dataset,
            perm = TestEnum.unexisting_perm,
        )
        self.assertTrue(result.allow_all)
        self.assertEqual(result.allowed_object_id_list, [])


        user = data_mocking.register_user({
            'username': 'test23_user',
            'email': 'test3@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project2.project_string_id,
            'no_roles': True,
        }, self.session)

        member3 = user.member
        # Assign role to 1 dataset
        RoleMemberObject.new(
            session = self.session,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetDefaultRoles.dataset_viewer,
            member_id = member3.id
        )
        result = self.policy_engine2.get_allowed_object_id_list(
            member = member3,
            object_type = ValidObjectTypes.dataset,
            perm = DatasetPermissions.dataset_view,
        )
        self.assertFalse(result.allow_all)

        self.assertTrue(ds1.id in result.allowed_object_id_list)
        self.assertTrue(restricted_ds.id not in result.allowed_object_id_list)

        # Assign role to revoked access dataset
        RoleMemberObject.new(
            session = self.session,
            object_id = restricted_ds.id,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetDefaultRoles.dataset_editor,
            member_id = member3.id
        )

        result = self.policy_engine2.get_allowed_object_id_list(
            member = member3,
            object_type = ValidObjectTypes.dataset,
            perm = DatasetPermissions.dataset_edit,
        )
        self.assertFalse(result.allow_all)
        self.assertTrue(restricted_ds.id in result.allowed_object_id_list)
