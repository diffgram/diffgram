from typing import List
from lark import Token
from sqlalchemy.orm import aliased
from sqlalchemy.sql.operators import in_op, comparison_op
from sqlalchemy.sql import Selectable
from sqlalchemy import Column
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import BooleanClauseList
from shared.database.source_control.file import File
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from sqlalchemy.sql.elements import FunctionFilter
from shared.database.tag.tag import DatasetTag, Tag
from shared.database.source_control.working_dir import WorkingDirFileLink
from sqlalchemy.sql.expression import and_, or_
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, CompareOperator
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind
from shared.query_engine.sql_alchemy_query_elements.query_elements import LabelQueryElement

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
    session: Session

    left_raw: Token or object
    compare_op_raw: Token or object
    right_raw: Token or object
    scalar_op: list or str or int or float
    query_op: QueryElement

    def __init__(self,
                 session: Session,
                 left_raw: Token or object,
                 right_raw: Token or object,
                 compare_op_raw: Token or object,
                 subquery: Selectable):
        self.session = session
        self.subquery = subquery
        self.left_raw = left_raw
        self.right_raw = right_raw
        self.compare_op_raw = compare_op_raw

    def set_compare_op_from_token(self, compare_op_token: Token):
        self.operator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        return self.compare_op

    def get_query_op(self) -> QueryElement:
        return self.query_op

    def set_scalar_and_query_op(self, 
                                entity_left: QueryEntity, 
                                entity_right: QueryEntity):
        if entity_left.type ='scaler':
            self.scalar_op = entity_left
            self.query_op = entity_right
        else:
            self.query_op = entity_right
            self.scalar_op = entity_left


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


class OrExpression:
    expression_list: List[AndExpression]
    sql_or_statement: BooleanClauseList

    def __init__(self, expression_list: List[AndExpression]):
        self.expression_list = expression_list
        sql_and_statements = [x.sql_and_statement for x in self.expression_list]
        self.sql_or_statement = or_(*sql_and_statements)
