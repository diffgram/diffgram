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
    reserved_sub_words: list = ['id', 'tag']
    def remove_plural(self):
        if type(self.key) == str:
            if self.key.endswith('s'):
                self.key = self.key[: - 1]

    def build_tree(self, token: Token) -> list:
        self.child_list = []
        if type(self.key) != str:
            return self.child_list
        list_items = token.value.split('.')
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

    def change_key_based_on_sub_elements(self):

        final_key = self.key
        if len(self.child_list) > 1:
            for i in range(len(self.child_list) - 1, -1, -1):
                child = self.child_list[i]
                if i == len(self.child_list) - 1:
                    continue

                if child.key in self.reserved_sub_words:
                    final_key += '_' + child.key
        self.key = final_key
    @staticmethod
    def new(token) -> 'QueryEntity':
        entity = QueryEntity()

        entity.set_key_from_token_with_unknown_type(token)

        entity.remove_plural()

        entity.build_tree(token)

        entity.change_key_based_on_sub_elements()

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
    reserved_words: List[str] = ['label', 'attribute', 'file', 'dataset_id', 'dataset_tag', 'list']

    def build_query(self, session: Session, token: Token) -> Selectable:
        raise NotImplementedError
    def determine_if_reserved_word(self, word: str):

        if word in self.reserved_words:
            return True

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
        from shared.query_engine.sql_alchemy_query_elements.dataset_tag import TagDatasetQueryElement
        from shared.query_engine.sql_alchemy_query_elements.file import FileQueryElement
        from shared.query_engine.sql_alchemy_query_elements.attribute import AttributeQueryElement
        from shared.query_engine.sql_alchemy_query_elements.dataset import DatasetQuery
        from shared.query_engine.sql_alchemy_query_elements.scalar import ScalarQueryElement
        from shared.query_engine.sql_alchemy_query_elements.labels import LabelsQueryElement
        query_element = QueryElement()

        entity = QueryEntity.new(token)

        query_element.query_entity = entity
        is_reserved_word = False
        if type(entity.key) == str and not has_quotes(entity.key):
            is_reserved_word = query_element.determine_if_reserved_word(entity.key)
            if not is_reserved_word:
                log['error'][
                    'is_reserved_word'] = f"Entity: {entity.key} is not valid. Valid options are {query_element.reserved_words}"
                return None, log
        else:
            entity.key = "scalar"
        string_query_class = {
            'label': LabelsQueryElement,
            'attribute': AttributeQueryElement,
            'file': FileQueryElement,
            'dataset_id': DatasetQuery,
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
