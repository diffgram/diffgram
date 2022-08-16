from shared.query_engine.query_elements import QueryElement

class DatasetQuery(QueryElement):

    def __init__(self):
        self.column = column

    # not clear what the init is doing here
    @staticmethod
    def create_from_token(
                session: Session, 
                project_id: int, 
                log: dict, 
                token: Token) -> ['DatasetQueryElement', dict]:

        dataset_property = token.value.split('.')[1]
        dataset_col = None
        if dataset_property == "id":
            dataset_col = WorkingDirFileLink.working_dir_id
        else:
            log['error']['not_supported'] = 'Dataset filters just support ID column.'
            return None, log
        return dataset_col, log


    def build_query(self, session) -> Selectable:

        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id)\
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id)\
            .filter(sql_compare_operator(value_1, value_2)).subquery(name = "ds_compare")
        return new_filter_subquery