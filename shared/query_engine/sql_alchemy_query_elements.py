from typing import List
from lark.tree import Token
from sqlalchemy.sql.operators import in_op, comparison_op
from sqlalchemy.sql import Subquery
from sqlalchemy.orm.session import Session
from shared.database.source_control.file import File
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
import operator

logger = get_shared_logger()


class QueryElement:
    and_statement: AndStatement or None
    or_statement: OrStatement or None
    expression: Expression or None
    compare_operator: CompareOperator or None
    subquery: Subquery

    def set_sql_operator_from_token(self, token: Token) -> CompareOperator:
        if token.value == '>':
            value = operator.gt
        if token.value == '<':
            value = operator.lt
        if token.value == '=':
            value = operator.eq
        if token.value == '!=':
            value = operator.ne
        if token.value == '>=':
            value = operator.ge
        if token.value == '<=':
            value = operator.le
        if token.value == 'in':
            value = in_op

        self.compare_operator = CompareOperator


class Expression:
    pass


class AndStatement:
    expression_list: List[Expression]


class OrStatement:
    expression_list: List[Expression]


class CompareOperator:
    operator_value: operator or comparison_op

    def __init__(self, operator_value: operator or comparison_op):
        self.operator_value = operator_value


class LabelQueryElement(QueryElement):
    subquery: Subquery

    def __init__(self, subquery: Subquery):
        self.subquery = subquery

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['LabelQueryElement', dict]:

        label_name = token.value.split('.')[1]

        label_file = File.get_by_label_name(session = session,
                                            label_name = label_name,
                                            project_id = project_id)
        if not label_file:
            # Strip underscores
            label_name = label_name.replace('_', ' ')
            label_file = File.get_by_label_name(session = session,
                                                label_name = label_name,
                                                project_id = project_id)
        if not label_file:
            error_string = f"Label {str(label_name)} does not exists"
            logger.error(error_string)
            log['error']['label_name'] = error_string
            return None, log
        instance_count_query = (session.query(FileStats.file_id).filter(
            FileStats.label_file_id == label_file.id
        ))
        result = LabelQueryElement(subquery = instance_count_query)
        return result, log

class AttributeQueryElement(QueryElement):

    def __init__(self, subquery: Subquery):
        self.subquery = attr_group_query

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['AttributeQueryElement', dict]:

        attr_group_name = token.value.split('.')[1]

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
        attr_group_query = (session.query(FileStats.file_id).filter(
            FileStats.attribute_template_group_id == attribute_group.id
        ))
        result = AttributeQueryElement(subquery=attr_group_query)
        return result, log
