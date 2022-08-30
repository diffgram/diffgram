from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from shared.database.source_control.dataset_perms import DatasetPermissions, DatasetRolesPermissions
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

    def test_get_allowed_object_id_list(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'project_roles': ['editor'],
            'member_id': self.member.id
        }, self.session)
        member2 = data_mocking.register_member(user, session = self.session)
        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        ds2 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        restricted_ds = data_mocking.create_directory({
            'project': self.project,
            'access_type': 'restricted',
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)

        class TestEnum(Enum):
            unexisting_perm = 'some_perm'

        result = self.policy_engine.get_allowed_object_id_list(
            member = self.member,
            object_type = ValidObjectTypes.dataset,
            perm = DatasetPermissions.dataset_view,
        )
        self.assertTrue(result.allow_all)
        self.assertEqual(result.allowed_object_id_list, [])

        # Test User has no perms
        result = self.policy_engine.get_allowed_object_id_list(
            member = member2,
            object_type = ValidObjectTypes.dataset,
            perm = TestEnum.unexisting_perm,
        )
        self.assertFalse(result.allow_all)
        self.assertEqual(result.allowed_object_id_list, [])
        # Assign role to 1 dataset
        RoleMemberObject.new(
            session = self.session,
            object_id = ds1.id,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetRolesPermissions.dataset_viewer,
            member_id = member2.id
        )
        result = self.policy_engine.get_allowed_object_id_list(
            member = member2,
            object_type = ValidObjectTypes.dataset,
            perm = TestEnum.unexisting_perm,
        )
        self.assertFalse(result.allow_all)
        self.assertEqual(len(result.allowed_object_id_list), 1)
        self.assertEqual(result.allowed_object_id_list[0], ds1.id)