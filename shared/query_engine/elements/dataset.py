from shared.query_engine.query_elements import QueryElement

class DatasetQuery(QueryElement):

    def __init__(self, column: Column):
        self.column = column

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


    @staticmethod
    def build_compare_expression(
                session: Session, 
                log: dict, 
                project_id: int, 
                value_1: any, 
                value_2: any,
                compare_op_token: Token) -> ['CompareExpression', dict]:

        query_op, scalar_op = CompareExpression.get_scalar_and_query_op(value_1, value_2)
        compare_op = CompareOperator.create_compare_operator_from_token(compare_op_token)
        sql_compare_operator = compare_op.operator_value
        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id)\
            .join(WorkingDirFileLink, WorkingDirFileLink.file_id == File.id)\
            .filter(sql_compare_operator(value_1, value_2)).subquery(name = "ds_compare")
        result = CompareExpression(operand1 = query_op,
                                   operand2 = scalar_op,
                                   operator = sql_compare_operator,
                                   subquery = new_filter_subquery)
        return result, log