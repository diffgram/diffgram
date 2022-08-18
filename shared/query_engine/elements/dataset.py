from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from sqlalchemy.sql import Selectable
from lark import Token
from sqlalchemy.orm.session import Session
from shared.database.source_control.working_dir import WorkingDirFileLink


class DatasetQuery(QueryElement):
    top_level_key = "dataset"

    def __init__(self):
        pass

    def build_query(self, session, token: Token) -> Selectable:
        dataset_property = token.value.split('.')[1]
        dataset_col = None
        if dataset_property == "id":
            dataset_col = WorkingDirFileLink.working_dir_id

        else:
            self.log['error']['not_supported'] = 'Dataset filters just support ID column.'
        self.column = dataset_col
        return self.column