from shared.query_engine.expressions.expressions import CompareExpression
from sqlalchemy.orm.session import Session
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable


class FileCompareExpression(CompareExpression):

    def build_expression_subquery(self, session) -> Selectable:
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_column = query_op.column
        sql_compare_operator = self.operator.operator_value

        AliasFile = aliased(File)
        new_filter_subquery = session.query(AliasFile.id).filter(sql_compare_operator(sql_column, raw_scalar_value)).subquery()
        self.subquery = new_filter_subquery
        return self.subquery
