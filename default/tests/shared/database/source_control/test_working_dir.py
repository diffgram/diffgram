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
            'email': 'testdirlist@test.com',
            'password': 'diffgram123',
            'project_string_id': self.project.project_string_id,
            'project_roles': ['editor'],
        }, self.session)

        ds1 = data_mocking.create_directory({
            'project': self.project,
            'user': self.project_data['users'][0],
            'files': []
        }, self.session)
        print('ds1', ds1.project_id, ds1.access_type, ds1.archived)
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
            member = user.member,
        )
        dirs_id_list = [x.id for x in dirs]
        self.assertEqual(len(dirs), 6)
        self.assertTrue(ds1.id in dirs_id_list)
        self.assertTrue(ds2.id in dirs_id_list)
        self.assertTrue(ds3.id in dirs_id_list)

        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset,
            default_role_name = DatasetDefaultRoles.dataset_viewer,
            member_id = user.member.id,
            object_id = ds_restricted.id
        )
        dirs = WorkingDir.list(
            session = self.session,
            project_id = self.project.id,
            member = user.member,
        )
        dirs_id_list = [x.id for x in dirs]
        self.assertEqual(len(dirs), 7)
        self.assertTrue(ds1.id in dirs_id_list)
        self.assertTrue(ds2.id in dirs_id_list)
        self.assertTrue(ds3.id in dirs_id_list)
        self.assertTrue(ds_restricted.id in dirs_id_list)
