from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.tag.tag import DatasetTag, Tag
from shared.database.source_control.file import File

class TagDatasetQueryElement(QueryElement):
    top_level_key = "dataset_tag"

    def __init__(self):
        pass

    @staticmethod
    def build_query() -> TagDatasetQueryElement:

        # Build tag ID list
        tag_id_list = []
        for tag_name in scalar_op:
            tag = Tag.get(session = session, name = tag_name, project_id = project_id)
            if tag:
                tag_id_list.append(tag.id)
        AliasFile = aliased(File)
        self.subquery = session.query(AliasFile.id)\
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id)\
            .join(DatasetTag, DatasetTag.dataset_id == WorkingDirFileLink.working_dir_id)\
            .filter(sql_compare_operator(value_1, tag_id_list)).subquery(name = "ds_tag_compare")
        return self.subquery
