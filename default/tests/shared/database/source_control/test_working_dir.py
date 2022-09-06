from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from shared.database.source_control.dataset_perms import DatasetPermissions, DatasetDefaultRoles
from enum import Enum


class TestWorkingDir(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestWorkingDir, self).setUp()
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

    def test_list(self):
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
        ds3 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        ds_restricted = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': [],
            'access_type': 'restricted'
        }, self.session)

        dirs = WorkingDir.list(
            session = self.session,
            project_id = self.project.id,
            member = member2,
        )

        self.assertEqual(len(dirs), 3)
        self.assertEqual(dirs[0].id, ds1.id)
        self.assertEqual(dirs[1].id, ds2.id)
        self.assertEqual(dirs[2].id, ds3.id)