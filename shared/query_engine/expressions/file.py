from shared.query_engine.expressions.expressions import CompareExpression
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.database.source_control.file import File
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Selectable
from shared.settings.env_adapter import EnvAdapter
from datetime import datetime, time
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()

class FileCompareExpression(CompareExpression):

    def build_expression_subquery(self, session) -> Selectable:
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_column = query_op.column
        sql_compare_operator = self.operator.operator_value
        AliasFile = aliased(File)
        if query_op.column in [File.created_time, File.time_last_updated]:
            format_string = "%Y-%m-%d"
            parsed_date = raw_scalar_value
            parsed_date = parsed_date.replace("'", "")
            parsed_date = parsed_date.replace('"', "")
            parsed_date = datetime.strptime(parsed_date, format_string)
            start_of_day = time(0, 0, 0)
            parsed_date = parsed_date.replace(hour = start_of_day.hour, minute = start_of_day.minute,
                                              second = start_of_day.second)

            self.expression = sql_compare_operator(sql_column, parsed_date)
        elif File.ann_is_complete == query_op.column:
            env_adapter = EnvAdapter()
            parsed_boolean = raw_scalar_value.replace("'", "")
            parsed_boolean = parsed_boolean.replace('"', "")
            parsed_boolean = env_adapter.bool(parsed_boolean)
            self.expression = sql_compare_operator(sql_column, parsed_boolean)
        else:
            self.expression = sql_compare_operator(sql_column, raw_scalar_value)


        return 
