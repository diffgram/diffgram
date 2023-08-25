from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, QueryEntity
from shared.query_engine.expressions.expressions import CompareExpression, CompareOperator
from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
from shared.query_engine.expressions.labels import LabelsCompareExpression
from lark import Token


class TestLabelsCompareExpression(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestLabelsCompareExpression, self).setUp()
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

    def test_build_expression_subquery(self):
        label = data_mocking.create_label({
            'name': 'apple',
        }, self.session)
        label_file = data_mocking.create_label_file({
            'label': label,
            'project_id': self.project.id
        }, self.session)
        expr, log = CompareExpression.new(
            session = self.session,
            left_raw = Token(value = 'label.apple', type_ = 'test'),
            right_raw = Token(value = '25', type_ = 'test'),
            compare_op_raw = Token(value = ">", type_ = 'test'),
            project_id = self.project.id,
            project = self.project,
            member = self.member,
            log = regular_log.default()
        )
        self.assertEqual(type(expr), LabelsCompareExpression)
        expr.build_expression_subquery(session = self.session)
        self.assertIsNotNone(expr.subquery)
