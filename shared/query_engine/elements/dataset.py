from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement

class DatasetQuery(QueryElement):

    def __init__(self):
        pass

    def build_query(self, session) -> Selectable:

        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id)\
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id)\
            .filter(sql_compare_operator(value_1, value_2)).subquery(name = "ds_compare")
        return new_filter_subquery