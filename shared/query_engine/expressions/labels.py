from shared.query_engine.expressions.expressions import CompareExpression
from sqlalchemy.orm.session import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from sqlalchemy.orm import Query
from shared.shared_logger import get_shared_logger
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind
from shared.database.source_control.file_stats import FileStats
from sqlalchemy.orm import Query
logger = get_shared_logger()


class LabelsCompareExpression(CompareExpression):

    def build_expression_subquery(self, session) -> Query:

        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_filter = query_op.subquery
        sql_compare_operator = self.operator.operator_value
        new_filter_subquery = sql_filter.filter(sql_compare_operator(FileStats.count_instances, raw_scalar_value)).subquery()
        self.subquery = new_filter_subquery
