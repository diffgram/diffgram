from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from shared.database.auth.member import Member
from shared.query_engine.query_creator import QueryCreator
from shared.query_engine.sqlalchemy_query_exectutor import SqlAlchemyQueryExecutor
from lark.lexer import Token
import operator
from sqlalchemy.sql.selectable import ScalarSelect
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.orm.query import Query
import flask
from sqlalchemy.orm.query import Query
from shared.query_engine.expressions.expressions import AndExpression, CompareExpression
class TestQueryCreator(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a meexchanism of setting up and tearing down the database should be created.
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

        self.credentials = b64encode("{}:{}".format(self.auth_api.client_id,
                                                    self.auth_api.client_secret).encode()).decode('utf-8')

    def test_start(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)

        query_string = 'labels.cars > 3'
        query_string2 = 'labels.apple > 3'
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            diffgram_query_obj = query_creator.create_query(query_string = query_string)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            result = executor.start((diffgram_query_obj.tree,))
            self.assertIsNotNone(execution_log['error'].get('label_name'))
            self.assertIsNone(result)
            self.assertFalse(executor.valid)

            # Correct case
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()

            self.assertEqual(len(execution_log['error'].keys()), 0)
            self.assertIsNone(result)
            self.assertTrue(executor.valid)

    def test_expr(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        query_string = 'labels.cars > 3'
        query_string2 = 'labels.apple > 3'
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            diffgram_query_obj = query_creator.create_query(query_string = query_string)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            result = executor.expr(diffgram_query_obj.tree.children[0])
        self.assertIsNotNone(execution_log['error'].get('label_name'))
        self.assertIsNone(result)
        self.assertFalse(executor.valid)

        # Correct case
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            result = executor.expr(diffgram_query_obj.tree.children[0])
        self.assertEqual(len(execution_log['error'].keys()), 0)
        self.assertIsNotNone(result)
        self.assertTrue(executor.valid)

    def test_term(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        query_string = 'labels.cars > 3'
        query_string2 = 'labels.apple > 3'
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            diffgram_query_obj = query_creator.create_query(query_string = query_string)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            local_tree = diffgram_query_obj.tree.children[0].children[0]
            executor.term(local_tree)
        self.assertIsNotNone(execution_log['error'].get('label_name'))
        self.assertFalse(executor.valid)

        # Correct case
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            local_tree = diffgram_query_obj.tree.children[0].children[0]
            result = executor.term(local_tree)
        self.assertEqual(len(execution_log['error'].keys()), 0)
        self.assertIsNotNone(local_tree.and_expression)
        self.assertEqual(type(local_tree.and_expression), AndExpression)
        self.assertTrue(executor.valid)

    def test_factor(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        query_string = 'labels.cars > 3'
        query_string2 = 'labels.apple > 3'
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            diffgram_query_obj = query_creator.create_query(query_string = query_string)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            result = executor.factor(diffgram_query_obj.tree.children[0].children[0].children[0])
        print(execution_log)
        self.assertIsNotNone(execution_log['error'].get('label_name'))
        self.assertIsNone(result)
        self.assertFalse(executor.valid)

        # Correct case
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            result = executor.factor(diffgram_query_obj.tree.children[0].children[0].children[0])
        self.assertEqual(len(execution_log['error'].keys()), 0)
        self.assertIsNotNone(result)
        self.assertTrue(executor.valid)

    def test__validate_expression(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_string = 'labels.x > 5'  # dummy query
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            diffgram_query_obj = query_creator.create_query(query_string = query_string)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)

            token = Token(value = 'something', type_ = 'dummy')
            token2 = Token(value = '5', type_ = 'dummy')
            operator = Token(value = '>', type_ = 'dummy')
            comp_expr, log = CompareExpression.new(
                session = self.session,
                left_raw = token,
                right_raw = token2,
                compare_op_raw = operator,
                project = self.project,
                member = self.member,
                log = regular_log.default()
            )
            value = executor._SqlAlchemyQueryExecutor__validate_expression(comp_expr)
            self.assertFalse(value, False)
            self.assertIsNotNone(executor.log['error'].get('compare_expr'))

            token = Token(value = 'labels.apple', type_ = 'dummy')
            token2 = Token(value = '5', type_ = 'dummy')
            operator = Token(value = '>', type_ = 'dummy')
            comp_expr, log = CompareExpression.new(
                session = self.session,
                left_raw = token,
                right_raw = token2,
                compare_op_raw = operator,
                project = self.project,
                member = self.member,
                log = regular_log.default()
            )
            print(comp_expr, log)
            executor.log['error'] = {}
            value = executor._SqlAlchemyQueryExecutor__validate_expression(comp_expr)
            self.assertTrue(value)
            self.assertEqual(len(executor.log['error'].keys()), 0)

            token = Token(value = 'file.sensor', type_ = 'dummy')
            token2 = Token(value = 'sensorA', type_ = 'dummy')
            operator = Token(value = '>', type_ = 'dummy')
            comp_expr, log = CompareExpression.new(
                session = self.session,
                left_raw = token,
                right_raw = token2,
                compare_op_raw = operator,
                project = self.project,
                member = self.member,
                log = regular_log.default()
            )
            executor.log['error'] = {}
            value = executor._SqlAlchemyQueryExecutor__validate_expression(comp_expr)
            self.assertFalse(value)
            self.assertEqual(len(executor.log['error'].keys()), 1)

    def test_compare_expr(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_string2 = 'labels.apple > 3'
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            # Correct case
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()
            local_tree = diffgram_query_obj.tree.children[0].children[0].children[0].children[0]
            executor.compare_expr(local_tree)
            self.assertEqual(len(execution_log['error'].keys()), 0)
            self.assertIsNotNone(local_tree)
            self.assertIsNotNone(local_tree.compare_expression)
            self.assertIsNotNone(type(local_tree.compare_expression), CompareExpression)
            self.assertTrue(executor.valid)

    def test_execute_query(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        with self.app.test_request_context():
            common_actions.add_auth_to_session(flask.session, self.project.users[0])
            query_string2 = 'labels.apple > 3'
            query_creator = QueryCreator(session = self.session, project = self.project, member = self.member)
            # Correct case
            diffgram_query_obj = query_creator.create_query(query_string = query_string2)
            executor = SqlAlchemyQueryExecutor(session = self.session, diffgram_query = diffgram_query_obj)
            sql_alchemy_query, execution_log = executor.execute_query()

            self.assertEqual(type(sql_alchemy_query), Query)
            self.assertEqual(len(executor.log['error'].keys()), 0)
