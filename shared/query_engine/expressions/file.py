from shared.query_engine.expressions.expressions import CompareExpression
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable
from shared.settings.env_adapter import EnvAdapter
from datetime import datetime, time

class FileCompareExpression(CompareExpression):

    def build_expression_subquery(self, session) -> Selectable:
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_column = query_op.column
        sql_compare_operator = self.operator.operator_value
        AliasFile = aliased(File)
        if File.created_time == query_op.column:
            format_string = "%Y-%m-%d"
            parsed_date = raw_scalar_value
            parsed_date = parsed_date.replace("'", "")
            parsed_date = parsed_date.replace('"', "")
            parsed_date = datetime.strptime(parsed_date, format_string)
            end_of_day = time(23, 59, 59)
            parsed_date = parsed_date.replace(hour = end_of_day.hour, minute = end_of_day.minute,
                                              second = end_of_day.second)

            new_filter_subquery = session.query(AliasFile.id).filter(
                sql_compare_operator(sql_column, parsed_date)).subquery()
        elif File.ann_is_complete == query_op.column:
            env_adapter = EnvAdapter()
            parsed_boolean = raw_scalar_value.replace("'", "")
            parsed_boolean = parsed_boolean.replace('"', "")
            parsed_boolean = env_adapter.bool(parsed_boolean)
            new_filter_subquery = session.query(AliasFile.id).filter(
                sql_compare_operator(sql_column, parsed_boolean)).subquery()
        else:
            new_filter_subquery = session.query(AliasFile.id).filter(sql_compare_operator(sql_column, raw_scalar_value)).subquery()

        self.subquery = new_filter_subquery
        return self.subquery
