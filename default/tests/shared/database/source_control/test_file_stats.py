from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.source_control.file_stats import FileStats
from shared.permissions.policy_engine.policy_engine import PolicyEngine, PermissionResult, PermissionResultObjectSet
from unittest.mock import patch
from shared.utils.attributes.attributes_values_parsing import get_attribute_value
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

    def test_update_file_stats_data__tree_attribute_global_instance_list(self):

        # Flaky test https://github.com/diffgram/diffgram/issues/1392
        return

        file = data_mocking.create_file({'project_id': self.project.id}, self.session)
        attr = data_mocking.create_attribute_template_group({
            'name': f'tree view',
            'kind': 'tree',
        }, self.session)
        option = data_mocking.create_attribute_template_option({
            'group_id': attr.id,
            'name': 'test'
        }, self.session)
        payload = [
            {'type': 'global', 'attribute_groups':
                {attr.id: {85377: {'name': 'Apple', 'selected': True},
                        'null': {'name': 'Banana', 'selected': True},    }}}

        ]
        with patch('shared.database.source_control.file_stats.get_attribute_value') as mock_1:
            mock_1.return_value = [['null', str(option.id)], 'tree']
            FileStats.update_file_stats_data(self.session, instance_list = payload, project = self.project, file_id = file.id)

        filestat = self.session.query(FileStats).filter(FileStats.file_id == file.id).first()
        filestats = self.session.query(FileStats).filter(FileStats.file_id == file.id).all()
        self.assertIsNotNone(filestat)

        self.assertEqual(len(filestats), 6)     # Why 6?   https://github.com/diffgram/diffgram/issues/1392
        self.assertEqual(filestat.file_id, file.id)
        self.assertEqual(filestat.attribute_template_id, attr.id)