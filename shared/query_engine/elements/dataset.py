from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from sqlalchemy.sql import Selectable
from sqlalchemy.orm import aliased
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink


class DatasetQuery(QueryElement):
    top_level_key = "dataset"

    def __init__(self):
        pass

    def build_query(self, session) -> Selectable:
        AliasFile = aliased(File)
        self.subquery = session.query(AliasFile.id) \
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id) \
            .filter(sql_compare_operator(value_1, value_2)).subquery(name = "ds_compare")
        return self.subquery
