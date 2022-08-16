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
from shared.database.tag.tag import DatasetTag, Tag
import operator
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind

logger = get_shared_logger()


class CompareOperator:
    operator_value: operator or comparison_op

    @staticmethod
    def create_compare_operator_from_token(token: Token) -> 'CompareOperator':
        string_operator_mapping = {
            '>': operator.gt,
            '<': operator.lt,
            '=': operator.eq,
            '!=': operator.ne,
            '>=': operator.ge,
            '<=': operator.le,
            'in': in_op,
        }
        value = string_operator_mapping[token.value]
        result = CompareOperator(operator_value = value)
        return result

    def __init__(self, operator_value: operator or comparison_op):
        self.operator_value = operator_value


class QueryElement:
    list_value: list
    column: Column or None
    subquery: Selectable

    token: Token
    type: None
    top_level_key: None

    def determine_if_reserved_word(self, word: str):

        reserved_words = ['labels', 'attribute', 'file', 'dataset', 'dataset_tag', 'list']
        if word in reserved_words:
            return True

    def get_sql_alchemy_query_value(self) -> Selectable \
        :
        if self.column:
            return self.column
        if self.subquery:
            return self.subquery
        if self.token:
            return self.token.value

    @staticmethod
    def __init__(
            session: Session,
            log: dict,
            project_id: int,
            formatted_entity: str,
            token: Token) -> 'QueryElement':
         """
            Generates a query element from the given entity type.
        :param session:
        :param log:
        :param project_id:
        :param entity_type:
        :param token:
        :return:
        """

        if type(formatted_entity) != str:
            self.is_reservered_word = False
            self.type = 'scaler'
            self.raw_token = token
            self.project_id = project_id
            return self.raw_token.value

        is_reservered_word = self.determine_if_reserved_word(formatted_entity)
        if not is_reservered_word:
            return False

        string_query_class = {
            'labels': LabelQueryElement,
            'attribute': AttributeQueryElement,
            'file': FileQueryElement,
            'dataset': DatasetQueryElement,
            'dataset_tag': TagDatasetQueryElement,
            'list': ListQueryElement
        }

        QueryClass = string_query_class.get(entity_type)

        if QueryClass is None:
            raise NotImplmentedException

        query_class = QueryClass()
        query_class.type = formatted_entity
        query_class.raw_token = token
        query_class.project_id = project_id
        query_class.is_reservered_word = is_reservered_word
        query_class.top_level_key = token.value.split('.')[1]

        return query_class



class LabelQueryElement(QueryElement):
    subquery: Selectable

    def __init__(self, subquery: Selectable
                 ):
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
        instance_count_query = session.query(FileStats.file_id).filter(
            FileStats.label_file_id == label_file.id
        )
        result = LabelQueryElement(subquery = instance_count_query)
        return result, log



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


