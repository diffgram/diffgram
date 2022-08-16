
class TagDatasetQueryElement(QueryElement):

    def __init__(self, column: Column):
        self.column = column


    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['DatasetQueryElement', dict]:

        dataset_property = token.value.split('.')[1]
        if dataset_property == "tag":
            dataset_col = DatasetTag.tag_id
        else:
            log['error']['not_supported'] = 'Dataset filters just support ID column.'
            return None, log
        return dataset_col, log


    @staticmethod
    def build_dataset_tag_compare_expression(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                                      compare_op_token: Token) -> ['CompareExpression', dict]:

        # Build tag ID list
        tag_id_list = []
        for tag_name in scalar_op:
            tag = Tag.get(session = session, name = tag_name, project_id = project_id)
            if tag:
                tag_id_list.append(tag.id)
        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id)\
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id)\
            .join(DatasetTag, DatasetTag.dataset_id == WorkingDirFileLink.working_dir_id)\
            .filter(sql_compare_operator(value_1, tag_id_list)).subquery(name = "ds_tag_compare")
        result = CompareExpression(operand1 = query_op,
                                   operand2 = scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log
