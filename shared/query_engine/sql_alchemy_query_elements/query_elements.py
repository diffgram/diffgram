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
from shared.query_engine.elements.tag import TagDatasetQueryElement
from shared.query_engine.elements.file import FileQueryElement
from shared.query_engine.elements.attribute import AttributeQueryElement
from shared.query_engine.elements.dataset import DatasetQuery

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


class QueryEntity:
    key: any            # any type, a scaler, or a string reserved word etc.
    parent_key: QueryEntity    
    kind: str           # scaler or reserved
    key_has_been_type_corrected: bool

    def remove_plural(self, entity.key):

        if type(self.key) == str:
            if self.key.endswith('s'):
                self.key = self.key[ : - 1]

    def build_tree(entity_string):
        if entity_string == "dataset":
            sub_value = token_value.value.split('.')[1]
            if sub_value == "tag":
                entity_string = "dataset_tag"
            else:
                entity_string = "dataset"
        return entity_string

    @staticmethod
    def cast_int_from_unknown_type(value : any):
        try:
            return int(value)
        except:
            return value

    def set_key_from_token_with_unknown_type(self, value):

        value = QueryEntity.cast_int_from_unknown_type(value)
        
        new_value = None

        if type(value) == int:
            new_value = value

        if type(value) == list:
            new_value = value

        if type(value) == str:
            new_value = token_value.split('.')[0]

        self.key = new_value
        self.key_has_been_type_corrected = True

        if type(value) not in [int, str, list]:
            raise NotImplmentedError


    def new(token):

        entity = QueryEntity()

        QueryEntity.set_key_from_token_with_unknown_type(token)

        self.remove_plural(entity.key)
        
        entity.build_tree()
        
        return entity



class QueryElement:
    list_value: list
    column: Column or None
    subquery: Selectable

    token: Token
    type: None
    top_level_key: None
    reserved_words: list
    query_entity: None
    query_entity_children: list

    def __init__():
        self.reserved_words = ['labels', 'attribute', 'file', 'dataset', 'dataset_tag', 'list']

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
        query_element = QueryElement()

        entity = QueryEntity.new(token)

        query_element.query_entity = entity
        query_element.query_entity_list = [] # SOMETHING

        if type(formatted_entity) == str:
            is_reserved_word = q.determine_if_reserved_word(formatted_entity)
            if not is_reserved_word:
                self.log['error']['is_reserved_word'] = f"Entity: {formatted_entity} is not valid. Valid options are {self.reserved_words}"
                return query_element
        else:
            formatted_entity = "scaler"

        string_query_class = {
            'labels': LabelQueryElement,
            'attribute': AttributeQueryElement,
            'file': FileQueryElement,
            'dataset': DatasetQuery,
            'dataset_tag': TagDatasetQueryElement,
            'scaler': ScalerQueryElement
        }

        QueryClass = string_query_class.get(formatted_entity)

        if QueryClass is None:
            raise NotImplementedError

        query_class = QueryClass()
        query_class.type = formatted_entity
        query_class.token = token
        query_class.project_id = project_id
        query_class.is_reserved_word = is_reserved_word
        query_class.top_level_key = token.value.split('.')[1]
        query_class.session = session
        query_class.log = log

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




