from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.tag.tag import DatasetTag, Tag
from shared.database.source_control.file import File
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Query
from lark import Token
from sqlalchemy.orm.session import Session


class TagDatasetQueryElement(QueryElement):
    top_level_key = "dataset_tag"

    def __init__(self):
        pass

    def build_query(self, session: Session, token: Token) -> Query:
        property = token.value.split('.')[1]
        if property == "tag":
            dataset_col = DatasetTag.tag_id
        self.column = dataset_col