from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.permissions.roles import ValidObjectTypes
from shared.permissions.policy_engine.policy_engine import PolicyEngine
from shared.database.source_control.dataset_perms import DatasetPermissions
from unittest.mock import Mock, patch
from shared.database.permissions.roles import ValidObjectTypes
from shared.database.source_control.dataset_perms import DatasetPermissions

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

    @patch("shared.database.source_control.working_dir.WorkingDir.get_dataset_viewing_permissions")
    def test_list(self, mock_get_dataset_viewing_permissions):
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

        mock_perm_result = Mock()
        mock_perm_result.allow_all = False
        mock_perm_result.allowed_object_id_list = [ds1.id, ds2.id, ds3.id]
        mock_get_dataset_viewing_permissions.return_value = mock_perm_result

        dirs = WorkingDir.list(
            session = self.session,
            project_id = self.project.id,
            member = user.member,
        )
        dirs_id_list = [x.id for x in dirs]
        self.assertEqual(len(dirs), 3)
        self.assertTrue(ds1.id in dirs_id_list)
        self.assertTrue(ds2.id in dirs_id_list)
        self.assertTrue(ds3.id in dirs_id_list)

        mock_perm_result.allowed_object_id_list.append(ds_restricted.id)

        dirs = WorkingDir.list(
            session = self.session,
            project_id = self.project.id,
            member = user.member,
        )
        dirs_id_list = [x.id for x in dirs]
        self.assertEqual(len(dirs), 4)
        self.assertTrue(ds1.id in dirs_id_list)
        self.assertTrue(ds2.id in dirs_id_list)
        self.assertTrue(ds3.id in dirs_id_list)
        self.assertTrue(ds_restricted.id in dirs_id_list)

    @patch("shared.database.source_control.working_dir.PolicyEngine")
    def test_get_dataset_viewing_permissions(self, MockPolicyEngine):
        # Arrange
        mock_policy_engine_instance = MockPolicyEngine.return_value
        mock_perm_result = {
            'allow_all': True,
            'allowed_object_id_list': []
        }
        mock_policy_engine_instance.get_allowed_object_id_list.return_value = mock_perm_result

        # Act
        result = WorkingDir.get_dataset_viewing_permissions(self.session, self.project, self.member)

        # Assert
        self.assertEqual(result, mock_perm_result)
        MockPolicyEngine.assert_called_once_with(session=self.session, project=self.project)
        mock_policy_engine_instance.get_allowed_object_id_list.assert_called_once_with(
            member=self.member,
            object_type=ValidObjectTypes.dataset,
            perm=DatasetPermissions.dataset_view
        )

    @patch("shared.database.source_control.working_dir.WorkingDir.get_dataset_viewing_permissions")
    def test_can_member_view_datasets_allow_all(self, mock_get_dataset_viewing_permissions):
        # Arrange
        candidate_dataset_ids = [1, 2, 3]
        mock_perm_result = Mock()
        mock_perm_result.allow_all = True
        mock_get_dataset_viewing_permissions.return_value = mock_perm_result

        # Act
        result = WorkingDir.can_member_view_datasets(self.session, self.project, self.member, candidate_dataset_ids)

        # Assert
        self.assertTrue(result)

    @patch("shared.database.source_control.working_dir.WorkingDir.get_dataset_viewing_permissions")
    def test_can_member_view_datasets_subset_allowed(self, mock_get_dataset_viewing_permissions):
        # Arrange
        candidate_dataset_ids = [1, 2]
        mock_perm_result = Mock()
        mock_perm_result.allow_all = False
        mock_perm_result.allowed_object_id_list = [2, 3, 1, 4]
        mock_get_dataset_viewing_permissions.return_value = mock_perm_result

        # Act
        result = WorkingDir.can_member_view_datasets(self.session, self.project, self.member, candidate_dataset_ids)

        # Assert
        self.assertTrue(result)

    @patch("shared.database.source_control.working_dir.WorkingDir.get_dataset_viewing_permissions")
    def test_can_member_view_datasets_not_allowed(self, mock_get_dataset_viewing_permissions):
        # Arrange
        candidate_dataset_ids = [1, 2]
        mock_perm_result = Mock()
        mock_perm_result.allow_all = False
        mock_perm_result.allowed_object_id_list = [1,3,4]
        mock_get_dataset_viewing_permissions.return_value = mock_perm_result

        # Act
        result = WorkingDir.can_member_view_datasets(self.session, self.project, self.member, candidate_dataset_ids)

        # Assert
        self.assertFalse(result)




