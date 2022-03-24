from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from methods.attribute.attribute_template_group_update import has_duplicate_children_on_tree_data


class TeseAttributeTemplateGroupUpdate(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TeseAttributeTemplateGroupUpdate, self).setUp()
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

    def test_has_duplicate_children_on_tree_data(self):
        no_dups_mock = [
            {
                'id': 1,
                'name': 'Applications :',
                'locked': True,
                'children': [
                    {'id': 2, 'name': 'Calendar : app'},
                    {'id': 3, 'name': 'Chrome : app'},
                    {'id': 4, 'name': 'Webstorm : app'},
                ],
            },
            {
                'id': 5,
                'name': 'Documents :',
                'children': [
                    {
                        'id': 6,
                        'name': 'vuetify :',
                        'children': [
                            {
                                'id': 7,
                                'name': 'src :',
                                'locked': True,
                                'children': [
                                    {'id': 8, 'name': 'index'},
                                    {'id': 9, 'name': 'bootstrap'},
                                ],
                            },
                        ],
                    },
                    {
                        'id': 10,
                        'name': 'material2 :',
                        'children': [
                            {
                                'id': 11,
                                'name': 'src :',
                                'children': [
                                    {'id': 12, 'name': 'v-btn : ts'},
                                    {'id': 13, 'name': 'v-card : ts'},
                                    {'id': 14, 'name': 'v-window : ts'},
                                ],
                            },
                        ],
                    },
                ],
            },
        ]

        result = has_duplicate_children_on_tree_data(no_dups_mock)

        self.assertFalse(result)

        with_dups_mock = [
            {
                'id': 1,
                'name': 'Applications :',
                'locked': True,
                'children': [
                    {'id': 2, 'name': 'Calendar : app'},
                    {'id': 3, 'name': 'Chrome : app'},
                    {'id': 4, 'name': 'Webstorm : app'},
                ],
            },
            {
                'id': 5,
                'name': 'Documents :',
                'children': [
                    {
                        'id': 6,
                        'name': 'vuetify :',
                        'children': [
                            {
                                'id': 7,
                                'name': 'src :',
                                'locked': True,
                                'children': [
                                    {'id': 8, 'name': 'index'},
                                    {'id': 8, 'name': 'index'},
                                    {'id': 9, 'name': 'bootstrap'},
                                ],
                            },
                        ],
                    },
                    {
                        'id': 10,
                        'name': 'material2 :',
                        'children': [
                            {
                                'id': 11,
                                'name': 'src :',
                                'children': [
                                    {'id': 12, 'name': 'v-btn : ts'},
                                    {'id': 13, 'name': 'v-card : ts'},
                                    {'id': 14, 'name': 'v-window : ts'},
                                ],
                            },
                        ],
                    },
                ],
            },
        ]

        result = has_duplicate_children_on_tree_data(no_dups_mock)

        self.assertTrue(result)
