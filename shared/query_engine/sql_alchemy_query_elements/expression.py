from typing import List
from lark.lark import Token
from sqlalchemy.sql.operators import in_op, comparison_op
from sqlalchemy.sql import Selectable
from sqlalchemy import Column
from sqlalchemy.orm.session import Session
from shared.database.source_control.file import File
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.tag.tag import DatasetTag
import operator
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement, CompareOperator
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind

logger = get_shared_logger()


class Expression(QueryElement):
    operand1: QueryElement
    operator: CompareOperator
    operand2: QueryElement

    def __init__(self, operand1: QueryElement, operand2: QueryElement, operator: CompareOperator, subquery: Selectable
                 ):
        self.subquery = subquery
        self.operand2 = operand2
        self.operand1 = operand1
        self.operator = operator

    def build_subquery_from_expression(self):
        pass

    @staticmethod
    def get_scalar_and_query_op(value_1: any, value_2: any) -> [Selectable, int or str]:
        if type(value_1) == int or type(value_1) == str:
            scalar_op = value_1
            query_op = value_2
        else:
            query_op = value_1
            scalar_op = value_2

        return query_op, scalar_op

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
    def build_dataset_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                         compare_op: str) -> ['Expression', dict]:
        query_op, scalar_op = Expression.get_scalar_and_query_op(value_1, value_2)
        compare_op = CompareOperator.create_sql_operator_from_token(scalar_op)
        sql_compare_operator = compare_op.operator_value
        new_filter_subquery = session.query(File.id).filter(sql_compare_operator(value_1, value_2)).subquery()
        return new_filter_subquery, log

    @staticmethod
    def build_file_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                         compare_op: str) -> ['Expression', dict]:
        query_op, scalar_op = Expression.get_scalar_and_query_op(value_1, value_2)
        compare_op = CompareOperator.create_sql_operator_from_token(scalar_op)
        sql_compare_operator = compare_op.operator_value
        new_filter_subquery = session.query(File.id).filter(sql_compare_operator(value_1, value_2)).subquery()
        result = Expression(subquery = new_filter_subquery)
        return result, log

    @staticmethod
    def build_attribute_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                           compare_op: str) -> ['Expression', dict]:
        query_op, scalar_op = Expression.get_scalar_and_query_op(value_1, value_2)
        attribute_kind, log = Expression.get_attribute_kind_from_string(
            session = session,
            log = log,
            project_id = project_id,
            string_value = scalar_op
        )
        sql_compare_operator = CompareOperator.create_sql_operator_from_token(scalar_op)
        file_stats_column = get_file_stats_column_from_attribute_kind(attribute_kind)
        if attribute_kind in ['radio', 'multiple_select', 'select', 'tree']:
            scalar_op = int(scalar_op)
        new_filter_subquery = (query_op.filter(sql_compare_operator(file_stats_column, scalar_op)).subquery())
        condition_operator = in_op(File.id, new_filter_subquery)
        result = Expression(subquery = condition_operator)
        return result, log

    @staticmethod
    def build_label_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any, compare_op: str) -> [
        'Expression', dict]:

        query_op, scalar_op = Expression.get_scalar_and_query_op(value_1, value_2)
        sql_compare_operator = CompareOperator.create_sql_operator_from_token(compare_op)
        new_filter_subquery = (query_op.filter(
            sql_compare_operator(FileStats.count_instances, scalar_op)).subquery()
                               )
        condition_operator = session.query(File.id).filter(in_op(File.id, new_filter_subquery)).subquery()
        result = Expression(operand1 = query_op, operand2 = scalar_op, operator = sql_compare_operator,
                            subquery = condition_operator)
        return result

    @staticmethod
    def build_expression_from_entity_type(session: Session, log: dict, project_id: int, entity_type: str, value_1: any,
                                          value_2: any, compare_op: str) -> ['Expression', log]:
        query_op, scalar_op = Expression.get_scalar_and_query_op(value_1, value_2)
        sql_compare_operator = CompareOperator.create_sql_operator_from_token(compare_op)
        expression = None
        build_expression_func_mapper = {
            "labels": Expression.build_label_compare_expression,
            "attribute": Expression.build_attribute_compare_expression,
            "dataset": Expression.build_dataset_compare_expression,
            "file": Expression.build_file_compare_expression,
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
            compare_op = compare_op
        )

class AndStatement:
    expression_list: List[Expression]


class OrStatement:
    expression_list: List[Expression]



class AndStatement:
    expression_list: List[Expression]


class OrStatement:
    expression_list: List[Expression]
