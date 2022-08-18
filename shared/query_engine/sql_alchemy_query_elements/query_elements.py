from lark.lark import Token
from sqlalchemy.sql.operators import in_op, comparison_op
from sqlalchemy.sql import Selectable
from sqlalchemy.orm import Query
from sqlalchemy import Column
from sqlalchemy.orm.session import Session
from shared.database.source_control.file import File
from shared.shared_logger import get_shared_logger
from shared.database.source_control.file_stats import FileStats
from typing import List
import operator
logger = get_shared_logger()

def has_quotes(s: str) -> bool:
    return (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'"))

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


class QueryEntity:
    key: any  # any type, a scaler, or a string reserved word etc.
    full_key: any  # any type, a scaler, or a string reserved word etc.
    parent_key: 'QueryEntity'
    kind: str  # scaler or reserved
    key_has_been_type_corrected: bool
    child_list: []

    def remove_plural(self):
        if type(self.key) == str:
            if self.key.endswith('s'):
                self.key = self.key[: - 1]

    def build_tree(self) -> list:
        self.child_list = []
        if type(self.key) != str:
            return self.child_list
        list_items = self.key.split('.')
        i = 0
        query_entity_list = [self]

        for item in reversed(list_items):
            ent = QueryEntity()
            ent.key = item
            if i > 0:
                ent.parent_key = query_entity_list[i - 1]
            if i < len(list_items) - 1:
                query_entity_list.append(ent)
                self.child_list.append(ent)
        return self.child_list

    @staticmethod
    def cast_int_from_unknown_type(value: any):
        try:
            return int(value)
        except:
            return value

    def set_key_from_token_with_unknown_type(self, token: Token):
        value = QueryEntity.cast_int_from_unknown_type(token.value)

        new_value = None
        full_key = None

        if type(value) == int:
            new_value = value

        if type(value) == list:
            new_value = value

        if type(value) == str:
            new_value = value.split('.')[0]
            full_key = value

        self.key = new_value
        self.full_key = full_key
        self.key_has_been_type_corrected = True

        if type(value) not in [int, str, list]:
            raise NotImplementedError

    @staticmethod
    def new(token) -> 'QueryEntity':
        entity = QueryEntity()

        entity.set_key_from_token_with_unknown_type(token)

        entity.remove_plural()

        entity.build_tree()

        return entity


class QueryElement:
    list_value: list
    raw_value: any
    column: Column or None
    subquery: Query
    project_id: int

    token: Token
    top_level_key: None
    log: dict
    query_entity: QueryEntity
    query_entity_children: List[QueryEntity]
    reserved_words: List[str] = ['labels', 'attribute', 'file', 'dataset', 'dataset_tag', 'list']

    def build_query(self, session: Session, token: Token) -> Selectable:
        raise NotImplementedError
    def determine_if_reserved_word(self, word: str):

        if word in self.reserved_words:
            return True

    def get_sql_alchemy_query_value(self) -> Selectable:
        if self.subquery:
            return self.subquery
        if self.token:
            return self.token.value

    @staticmethod
    def new(session: Session,
            log: dict,
            project_id: int,
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
        from shared.query_engine.sql_alchemy_query_elements.tag import TagDatasetQueryElement
        from shared.query_engine.sql_alchemy_query_elements.file import FileQueryElement
        from shared.query_engine.sql_alchemy_query_elements.attribute import AttributeQueryElement
        from shared.query_engine.sql_alchemy_query_elements.dataset import DatasetQuery
        from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
        query_element = QueryElement()

        entity = QueryEntity.new(token)

        query_element.query_entity = entity
        is_reserved_word = False

        if type(entity.key) == str and not has_quotes(entity.key):
            is_reserved_word = query_element.determine_if_reserved_word(entity.key)
            if not is_reserved_word:
                log['error'][
                    'is_reserved_word'] = f"Entity: {entity.key} is not valid. Valid options are {query_element.reserved_words}"
                return query_element, log
        else:
            entity.key = "scalar"
        string_query_class = {
            'labels': LabelQueryElement,
            'attribute': AttributeQueryElement,
            'file': FileQueryElement,
            'dataset': DatasetQuery,
            'dataset_tag': TagDatasetQueryElement,
            'scalar': ScalarQueryElement
        }

        QueryClass = string_query_class.get(entity.key)

        if QueryClass is None:
            raise NotImplementedError

        query_class = QueryClass()
        query_class.query_entity = entity
        query_class.token = token
        query_class.project_id = project_id
        query_class.is_reserved_word = is_reserved_word
        query_class.session = session
        query_class.log = log

        query_class.build_query(session = session, token = token)

        return query_class, log


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
