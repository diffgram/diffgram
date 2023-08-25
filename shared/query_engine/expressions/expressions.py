from typing import List
from lark import Token
from sqlalchemy.sql import Selectable
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import BooleanClauseList
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from sqlalchemy.sql.elements import FunctionFilter
from sqlalchemy.sql.expression import and_, or_, BinaryExpression
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, CompareOperator, QueryEntity
from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
from shared.database.project import Project

from shared.regular import regular_log

logger = get_shared_logger()


class Factor:
    filter_value: FunctionFilter

    def __init__(self, filter_value: FunctionFilter):
        self.filter_value = filter_value


class CompareExpression:
    query_left: QueryElement
    operator: CompareOperator
    query_right: QueryElement
    subquery: Selectable
    expression: BinaryExpression
    left_raw: Token or object
    compare_op_raw: Token or object
    right_raw: Token or object
    scalar_op: QueryElement
    query_op: QueryElement
    project_id: int
    project: Project
    member: any # TODO: Is there a type for this?
    log: dict

    def __init__(self,
                 session: Session,
                 project: Project,
                 member: any,
                 left_raw: Token or object,
                 right_raw: Token or object,
                 compare_op_raw: Token or object):
        self.session = session
        self.left_raw = left_raw
        self.right_raw = right_raw
        self.compare_op_raw = compare_op_raw

        # TODO: Look at other cleanups that can be done now that this is here
        self.member = member
        self.project = project

    @staticmethod
    def determine_entity_from_query_operator(left_elm: QueryElement, right_elm: QueryElement) -> str:
        if type(left_elm) == ScalarQueryElement:
            result = right_elm.query_entity.key
        else:
            result = left_elm.query_entity.key
        return result

    @staticmethod
    def new(session: Session,
            project: Project,
            member: any,
            left_raw: Token,
            compare_op_raw: Token,
            right_raw: Token,
            project_id: int,
            log: dict) -> ['CompareExpression', dict]:
        from shared.query_engine.expressions.dataset import DatasetCompareExpression
        from shared.query_engine.expressions.file import FileCompareExpression
        from shared.query_engine.expressions.attribute import AttributeCompareExpression
        from shared.query_engine.expressions.dataset_tag import DatasetTagCompareExpression
        from shared.query_engine.expressions.labels import LabelsCompareExpression
        query_element_left, log = QueryElement.new(
            session = session,
            log = log,
            project_id = project_id,
            token = left_raw
        )
        if regular_log.log_has_error(log):
            logger.error(log)
            return None, log

        query_element_right, log = QueryElement.new(
            session = session,
            log = log,
            project_id = project_id,
            token = right_raw
        )

        if regular_log.log_has_error(log):
            logger.error(log)
            return None, log
        query_entity_key = CompareExpression.determine_entity_from_query_operator(query_element_left,
                                                                                  query_element_right)
        string_query_class = {
            'dataset_id': DatasetCompareExpression,
            'file': FileCompareExpression,
            'attribute': AttributeCompareExpression,
            'label': LabelsCompareExpression,
            'dataset_tag': DatasetTagCompareExpression,
        }
        CompareExpClass = string_query_class.get(query_entity_key)
        if CompareExpClass is None:
            raise NotImplementedError

        compare_expression = CompareExpClass(
            session = session,
            project = project,
            member = member,
            left_raw = left_raw,
            compare_op_raw = compare_op_raw,
            right_raw = right_raw
        )
        compare_expression.query_left = query_element_left
        compare_expression.project_id = project_id
        compare_expression.query_right = query_element_right
        compare_expression.log = log
        compare_expression.set_compare_op_from_token(compare_expression.compare_op_raw)
        compare_expression.set_scalar_and_query_op()
        return compare_expression, log

    def build_expression_subquery(self, session: Session):
        raise NotImplementedError

    def set_compare_op_from_token(self, compare_op_token: Token) -> CompareOperator:
        self.operator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        return self.operator

    def set_scalar_and_query_op(self):
        if type(self.query_left) == ScalarQueryElement:
            self.scalar_op = self.query_left
            self.query_op = self.query_right
        else:
            self.query_op = self.query_left
            self.scalar_op = self.query_right

    def build_label_compare_expression(self,
                                       log: dict,
                                       project_id: int,
                                       value_1: any,
                                       value_2: any,
                                       compare_op_token: Token) -> ['CompareExpression', dict]:
        if not self.query_op or not self.scalar_op:
            log['error']['scalar_query_ops'] = 'scalar_op or query_op are None in the compare expression'
            return None, log
        compare_operator: CompareOperator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        sql_compare_operator = compare_operator.operator_value
        label_query_element: QueryElement = self.query_op
        new_filter_subquery = label_query_element.subquery.filter(
            sql_compare_operator(FileStats.count_instances, self.scalar_op)).subquery()
        result = CompareExpression(operand1 = self.query_op,
                                   operand2 = self.scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log


class AndExpression:
    expression_list: List[CompareExpression]
    sql_and_statement: BooleanClauseList

    def __init__(self, expression_list: List[CompareExpression]):
        self.expression_list = expression_list
        self.sql_and_statement = and_(*expression_list)

    def add_expression(self, selectable_expr_elm: Selectable):
        self.expression_list.append(selectable_expr_elm)
        self.sql_and_statement = and_(*self.expression_list)


class OrExpression:
    expression_list: List[AndExpression]
    sql_or_statement: BooleanClauseList

    def __init__(self, expression_list: List[AndExpression]):
        self.expression_list = expression_list
        sql_and_statements = [x.sql_and_statement for x in self.expression_list]
        if len(self.expression_list) == 0:
            self.sql_or_statement = or_(True)
        else:

            self.sql_or_statement = or_(*sql_and_statements)

    def add_expression(self, selectable_expr_elm: AndExpression):
        self.expression_list.append(selectable_expr_elm)
        sql_and_statements = [x.sql_and_statement for x in self.expression_list]
        if len(self.expression_list) == 0:
            self.sql_or_statement = or_(True)
        else:

            self.sql_or_statement = or_(*sql_and_statements)