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

class CompareExpression():
    query_left: QueryElement
    operator: CompareOperator
    query_right: QueryElement
    subquery: Selectable

    left_raw: Any
    compare_op_raw: Any
    right_raw: Any

    def __init__(self, operand1: QueryElement, operand2: QueryElement, operator: CompareOperator, subquery: Selectable
                 ):
        self.subquery = subquery
        self.operand2 = operand2
        self.operand1 = operand1
        self.operator = operator

    def build_subquery_from_expression(self):
        pass


    def set_scalar_and_query_op(value_1: any, value_2: any) -> [Selectable, int or str]:
        if type(value_1) == int or type(value_1) == str:
            self.scalar_op = value_1
            self.query_op = value_2
        else:
            self.query_op = value_1
            self.scalar_op = value_2


    @staticmethod
    def get_attribute_kind_from_string(session: Session, log: dict, project_id: int, string_value: str) -> [str, dict]:
        attr_group_name = string_value.split('.')[1]
        attribute_group = Attribute_Template_Group.get_by_name_and_project(
            session = session,
            name = attr_group_name,
            project_id = project_id
        )

        if not attribute_group:
            # Strip underscores
            attr_group_name = attr_group_name.replace('_', ' ')
            attribute_group = Attribute_Template_Group.get_by_name_and_project(
                session = session,
                name = attr_group_name,
                project_id = project_id
            )
        if not attribute_group:
            error_string = f"Attribute Group {str(attr_group_name)} does not exists"
            logger.error(error_string)
            log['error']['attr_group_name'] = error_string
            return None, log
        return attribute_group.kind, log



    @staticmethod
    def build_file_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                      compare_op_token: Token) -> ['CompareExpression', dict]:
        query_op, scalar_op = CompareExpression.get_scalar_and_query_op(value_1, value_2)
        compare_op = CompareOperator.create_compare_operator_from_token(compare_op_token)
        sql_compare_operator = compare_op.operator_value
        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id).filter(sql_compare_operator(value_1, value_2)).subquery()
        result = CompareExpression(operand1 = query_op,
                                   operand2 = scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log

    @staticmethod
    def build_attribute_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                           compare_op_token: Token) -> ['CompareExpression', dict]:
        query_op, scalar_op = CompareExpression.get_scalar_and_query_op(value_1, value_2)
        attribute_kind, log = CompareExpression.get_attribute_kind_from_string(
            session = session,
            log = log,
            project_id = project_id,
            string_value = scalar_op
        )
        sql_compare_operator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        file_stats_column = get_file_stats_column_from_attribute_kind(attribute_kind)
        if attribute_kind in ['radio', 'multiple_select', 'select', 'tree']:
            scalar_op = int(scalar_op)
        new_filter_subquery = query_op.filter(sql_compare_operator(file_stats_column, scalar_op)).subquery()
        result = CompareExpression(operand1 = query_op,
                                   operand2 = scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log

    @staticmethod
    def build_label_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                       compare_op_token: Token) -> [
        'CompareExpression', dict]:

        query_op, scalar_op = CompareExpression.get_scalar_and_query_op(value_1, value_2)
        compare_operator: CompareOperator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        sql_compare_operator = compare_operator.operator_value
        label_query_element: LabelQueryElement = query_op
        new_filter_subquery = label_query_element.subquery.filter(sql_compare_operator(FileStats.count_instances, scalar_op)).subquery()
        result = CompareExpression(operand1 = query_op,
                                   operand2 = scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log

    @staticmethod
    def build_expression_from_entity_type(session: Session, log: dict, project_id: int, entity_type: str, value_1: any,
                                          value_2: any, compare_op: str) -> ['CompareExpression', dict]:
        expression = None
        build_expression_func_mapper = {
            "labels": CompareExpression.build_label_compare_expression,
            "attribute": CompareExpression.build_attribute_compare_expression,
            "dataset": CompareExpression.build_dataset_compare_expression,
            "file": CompareExpression.build_file_compare_expression,
            "dataset_tag": CompareExpression.build_dataset_tag_compare_expression,
        }
        expression_builder_func = build_expression_func_mapper.get(entity_type)
        if not expression_builder_func:
            msg = f'Invalid entity type {entity_type}'
            raise Exception(msg)
        expression, log = expression_builder_func(
            session = session,
            value_1 = value_1,
            value_2 = value_2,
            log = log,
            project_id = project_id,
            compare_op_token = compare_op,
        )
        return expression, log


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
