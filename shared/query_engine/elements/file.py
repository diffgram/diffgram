from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable


class FileQueryElement(QueryElement):
    top_level_key = "file"

    def __init__(self):
        pass

    def build_metadata_query(self, session: Session, file_key: str):
        column = File.file_metadata[file_key].astext
        self.subquery = session.query(File.id).filter(File.file_metadata[file_key].astext).subquery()
        return self.subquery

    def build_query(self, session: 'Session', file_key: str) -> Selectable:
        file_key = self.token.value.split('.')[1]
        return self.build_metadata_query(session, file_key = file_key)
