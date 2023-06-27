from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable
from lark import Token


class FileQueryElement(QueryElement):
    top_level_key = "file"

    def __init__(self):
        pass

    def build_metadata_query(self, session: Session, file_key: str) -> Selectable:
        self.column = File.file_metadata[file_key].astext
        self.subquery = session.query(File.id).filter(File.file_metadata[file_key].astext).subquery()
        return self.subquery

    def build_query_reserved_columns(self, session: Session, column_name: str) -> Selectable:
        self.column = getattr(File, column_name)
        self.subquery = session.query(File.id).filter(self.column).subquery()
        return self.subquery

    def build_query(self, session: 'Session', token: Token) -> Selectable:
        file_key = token.value.split('.')[1]
        reserved_columns = ['created_time', 'type', 'ann_is_complete', 'original_filename', 'task_id', 'frame_number', 'parent_id']
        if file_key not in reserved_columns:
            return self.build_metadata_query(session, file_key = file_key)
        else:
            return self.build_query_reserved_columns(session = session, column_name = file_key)