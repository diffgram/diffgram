from methods.regular.regular_api import *
from default.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from unittest.mock import patch
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, QueryEntity
from shared.query_engine.expressions.expressions import CompareExpression, CompareOperator
from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
from shared.query_engine.expressions.dataset import DatasetCompareExpression
from lark import Token

class TestDatasetCompareExpression(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestDatasetCompareExpression, self).setUp()
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

    def initialize_compare_expression(self):
        expr, log = CompareExpression.new(
            session = self.session,
            left_raw = Token(value = 'dataset.id', type_ = 'test'),
            right_raw = Token(value = ['25'], type_ = 'test'),
            compare_op_raw = Token(value = '=', type_ = 'test'),
            project = self.project,
            member = self.member,
            log = regular_log.default()
        )

        return expr, log

    @patch("shared.query_engine.expressions.dataset.WorkingDir")
    def test_build_expression_subquery(self, MockWorkingDir):
        # Arrange
        MockWorkingDir.can_member_view_datasets.return_value = True
        expr, log = self.initialize_compare_expression()

        # Act
        expr.build_expression_subquery(session = self.session)

        # Assert
        self.assertEqual(type(expr), DatasetCompareExpression)
        MockWorkingDir.can_member_view_datasets.assert_called_once_with(session = self.session, project = self.project, dataset_ids = ['25'], member = self.member)
        self.assertIsNotNone(expr.expression)
        self.assertEqual(log['error'], {})

    @patch("shared.query_engine.expressions.dataset.WorkingDir")
    def test_build_expression_subquery_unauthorized(self, MockWorkingDir):
        # Arrange
        MockWorkingDir.can_member_view_datasets.return_value = False
        expr, log = self.initialize_compare_expression()

        # Act
        expr.build_expression_subquery(session = self.session)

        # Assert
        self.assertEqual(type(expr), DatasetCompareExpression)
        MockWorkingDir.can_member_view_datasets.assert_called_once_with(session = self.session, project = self.project, dataset_ids = ['25'], member = self.member)
        self.assertEqual(log['error']['unauthorized'], 'You do not have access to these datasets')
        self.assertFalse(hasattr(expr, 'expression'))
