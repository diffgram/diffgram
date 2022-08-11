from typing import List
from lark.tree import Token
from sqlalchemy.sql.operators import in_op, comparison_op
from sqlalchemy.sql import Subquery
from sqlalchemy import Column
from sqlalchemy.orm.session import Session
from shared.database.source_control.file import File
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.tag.tag import DatasetTag
import operator

logger = get_shared_logger()


class AndStatement:
    expression_list: List[Expression]


class OrStatement:
    expression_list: List[Expression]


class CompareOperator:
    operator_value: operator or comparison_op

    def __init__(self, operator_value: operator or comparison_op):
        self.operator_value = operator_value


class QueryElement:
    and_statement: AndStatement or None
    or_statement: OrStatement or None
    expression: Expression or None
    list_value: list
    column: Column or None
    subquery: Subquery
    token: Token

    def get_sql_alchemy_query_value(self) -> Column or Subquery or Expression or AndStatement or OrStatement or str:
        if self.column:
            return self.column
        if self.subquery:
            return self.subquery
        if self.token:
            return self.toke.value

    def generate_query_element(self,
                               session: Session,
                               log: dict,
                               project_id: int,
                               entity_type: str,
                               token: Token) -> ['QueryElement', dict]:
        """
            Generates a query element from the given entity type.
        :param session:
        :param log:
        :param project_id:
        :param entity_type:
        :param token:
        :return:
        """
        if entity_type == 'labels':
            query_element, log = LabelQueryElement.create_from_token(
                session = session,
                log = log,
                project_id = project_id,
                token = token
            )
        if entity_type == 'attribute':
            query_element, log = AttributeQueryElement.create_from_token(
                session = session,
                log = log,
                project_id = project_id
                ,
                token = token
            )
        elif entity_type == 'file':
            # Case for metadata
            query_element, log = FileQueryElement.create_from_token(
                session = session,
                log = log,
                project_id = project_id
                ,
                token = token
            )
        elif entity_type == 'dataset':
            query_element, log = DatasetQueryElement.create_from_token(
                session = session,
                log = log,
                project_id = project_id
                ,
                token = token
            )
        elif entity_type == 'tag':
            raise NotImplementedError

        elif entity_type == list:
            query_element, log = ListQueryElement.create_from_token(
                session = session,
                log = log,
                project_id = project_id,
                token = token
            )
        else:
            return token.value

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
        self.subquery = subquery

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['AttributeQueryElement',
                                                                                          dict]:

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
        result = AttributeQueryElement(subquery = attr_group_query)
        return result, log


class DatasetQueryElement(QueryElement):

    def __init__(self, column: Column):
        self.column = column

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['DatasetQueryElement', dict]:

        dataset_property = token.value.split('.')[1]
        dataset_col = None
        if dataset_property == "id":
            dataset_col = WorkingDirFileLink.working_dir_id
        else:
            log['error']['not_supported'] = 'Dataset filters just support ID column.'
            return None, log
        return dataset_col, log


class FileQueryElement(QueryElement):

    def __init__(self, column: Column):
        self.column = column

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['FileQueryElement', dict]:
        file_key = token.value.split('.')[1]
        column = None
        if file_key == 'type':
            column = File.type
        else:
            # Any non-default columns are considered as metadata.
            column = File.file_metadata[file_key].astext
        query_element = FileQueryElement(column = column)
        return query_element, log


class ListQueryElement(QueryElement):

    def __init__(self, list_value: list):
        self.list_value = list_value

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['ListQueryElement', dict]:
        # Token value here is already a list. Parsed by array() function on sqlalchemy_query_executor.py
        list_value = token.value
        if type(list_value) != list:
            log['error']['list_value'] = f'Invalid token value {token.value}. Not a list.'
            return None, log
        query_element = ListQueryElement(list_value = list_value)
        return query_element, log


class TokenQueryElement(QueryElement):

    def __init__(self, token: Token):
        self.token = token

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['ListQueryElement', dict]:
        # Token value here is already a list. Parsed by array() function on sqlalchemy_query_executor.py
        list_value = token.value
        if type(list_value) != list:
            log['error']['list_value'] = f'Invalid token value {token.value}. Not a list.'
            return None, log
        query_element = ListQueryElement(list_value = list_value)
        return query_element, log


class Expression(QueryElement):
    operand1: QueryElement
    operator: CompareOperator
    operand2: QueryElement

    @staticmethod
    def build_expression_from_operands() -> Expression:
        pass


