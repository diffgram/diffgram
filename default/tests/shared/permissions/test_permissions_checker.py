from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import Role, RoleMemberObject, ValidObjectTypes
from shared.permissions.PermissionsChecker import PermissionsChecker


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
    def test_member_has_any_project_role(self):

        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.project.name,
            object_id = self.project.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )

        result = PermissionsChecker.member_has_any_project_role(
            session = self.session,
            member_id = self.member.id,
            roles = ['viewer_test'],
            project_id = self.project.id,
        )
        self.assertFalse(result)

        result = PermissionsChecker.member_has_any_project_role(
            session = self.session,
            member_id = self.member.id,
            roles = ['editor_test'],
            project_id = self.project.id
        )
        self.assertTrue(result)

        result = PermissionsChecker.member_has_any_project_role(
            session = self.session,
            member_id = self.member.id,
            roles = ['editor_test', 'blablab', 'viewer_test'],
            project_id = self.project.id
        )
        self.assertTrue(result)

    def test_get_allowed_object_id_list(self):
        user = data_mocking.register_user({
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'diffgram123',
            'project_string_id': 'myproject',
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
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset.name,
            object_id = ds1.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset.name,
            object_id = ds2.id,
            role_id = self.editor_role.id,
            member_id = self.member.id
        )
        RoleMemberObject.new(
            session = self.session,
            object_type = ValidObjectTypes.dataset.name,
            object_id = ds3.id,
            role_id = self.editor_role.id,
            member_id = member2.id
        )

        result = PermissionsChecker.get_allowed_object_id_list(
            session = self.session,
            member = self.member,
            object_type = ValidObjectTypes.dataset.name,
            perm = 'an_unexisting_perm'
        )
        self.assertEqual(result, [])