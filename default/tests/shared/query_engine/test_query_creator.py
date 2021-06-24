from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from shared.query_engine.query_creator import QueryCreator
from shared.query_engine.diffgram_query import DiffgramQuery
import flask


class TestQueryCreator(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestQueryCreator, self).setUp()
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

    def test_get_suggestions(self):
        query_str = ''
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            creator = QueryCreator(self.session, self.project, self.member)
            result, type = creator.get_suggestions(query_string = query_str)
            self.assertTrue('labels' in result)
            self.assertTrue('file' in result)
            self.assertEqual(type, 'entities')
            label = data_mocking.create_label({
                'name': 'apple',
            }, self.session)
            label_file = data_mocking.create_label_file({
                'label': label,
                'project_id': self.project.id
            }, self.session)
            label2 = data_mocking.create_label({
                'name': 'car',
            }, self.session)
            label_file2 = data_mocking.create_label_file({
                'label': label2,
                'project_id': self.project.id
            }, self.session)
            label3 = data_mocking.create_label({
                'name': 'person',
            }, self.session)
            label_file3 = data_mocking.create_label_file({
                'label': label3,
                'project_id': self.project.id
            }, self.session)

            query_str = 'labels.'
            result, type = creator.get_suggestions(query_string = query_str)

            self.assertEqual(type, 'labels')
            self.assertTrue('apple' in result)
            self.assertTrue('car' in result)
            self.assertTrue('person' in result)

            query_str = 'file.'
            result, type = creator.get_suggestions(query_string = query_str)

            self.assertEqual(type, 'labels')

            # query_str = 'instance.'
            # result, type = creator.get_suggestions(query_string = query_str)
            # self.assertTrue('type' in result)
            # self.assertTrue('count' in result)
            # self.assertTrue('tag' in result)
            # self.assertTrue('model' in result)
            # self.assertTrue('model_run' in result)
            #
            # query_str = 'issues.'
            # result, type = creator.get_suggestions(query_string = query_str)
            # self.assertTrue('status' in result)
            # self.assertTrue('count' in result)

    def test_create_query(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        query_str = 'labels.apple > 0'
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            result = creator.create_query(query_string = query_str)
            self.assertTrue(type(result) == DiffgramQuery)
            self.assertEqual(result.tree.data, 'start')
            self.assertEqual(result.tree.children[0].data, 'expr')
            self.assertEqual(result.tree.children[0].children[0].data, 'term')
            self.assertEqual(result.tree.children[0].children[0].children[0].data, 'factor')
            self.assertEqual(result.tree.children[0].children[0].children[0].children[0].data, 'compare_expr')
