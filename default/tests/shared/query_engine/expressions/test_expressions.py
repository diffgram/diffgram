from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, QueryEntity
from shared.query_engine.expressions.expressions import CompareExpression, CompareOperator
from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
from shared.query_engine.sql_alchemy_query_elements.labels import LabelsQueryElement
from lark import Token
class TestCompareExpression(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestCompareExpression, self).setUp()
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

    def test_determine_entity_from_query_operator(self):

        left = ScalarQueryElement()
        right = QueryElement()
        left.query_entity = QueryEntity.new(token = Token(value = 'test_left', type_ = 'test'))
        right.query_entity = QueryEntity.new(token = Token(value = 'test_right', type_ = 'test_right'))

        result = CompareExpression.determine_entity_from_query_operator(left, right)

        self.assertEqual(result, "test_right")

    def test_new(self):
        label = data_mocking.create_label({
            'name': 'car',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        # Error reserved keywords case
        result, log = CompareExpression.new(
            session = self.session,
            left_raw = Token(value = 'value_left', type_ = "test"),
            right_raw = Token(value = 'value_right', type_ = "test"),
            compare_op_raw = Token(value = 'value_op', type_ = "test"),
            project = self.project,
            member = self.member,
            log = regular_log.default()
        )

        self.assertEqual(None, result)
        self.assertEqual(len(log['error'].keys()), 1)
        self.assertEqual(list(log['error'].keys()), ['is_reserved_word'])
        log = regular_log.default()
        # Success case
        result, log = CompareExpression.new(
            session = self.session,
            left_raw = Token(value = 'labels.car', type_ = "test"),
            right_raw = Token(value = '8', type_ = "test"),
            compare_op_raw = Token(value = '>=', type_ = "test"),
            project = self.project,
            member = self.member,
            log = regular_log.default()
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertIsNotNone(result.query_left)
        self.assertIsNotNone(result.query_right)
        self.assertIsNotNone(result.operator)
        self.assertEqual(type(result.query_left), LabelsQueryElement)
        self.assertEqual(type(result.query_right), ScalarQueryElement)
        self.assertEqual(type(result.operator), CompareOperator)