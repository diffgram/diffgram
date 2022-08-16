from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement

class FileQueryElement(QueryElement):

    def __init__(self):
        pass

    def build_metadata_query(self):
        column = File.file_metadata[file_key].astext
        self.subquery = session.query(File.id).filter(File.file_metadata[file_key].astext).subquery()
        return self.subquery


    def build_type_query(self):
        AliasFile = aliased(File)
        self.subquery = session.query(AliasFile.id).filter(sql_compare_operator(value_1, value_2)).subquery()
        return self.subquery


    def build_query(session: Session) -> Selectable:

        if self.top_level_key == 'type':
            return self.build_type_query()
        else:
            return self.build_metadata_query()