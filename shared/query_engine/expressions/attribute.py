from shared.query_engine.expressions.expressions import CompareExpression
from sqlalchemy.orm.session import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from sqlalchemy.orm import Query
from shared.shared_logger import get_shared_logger
from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from shared.utils.attributes.attributes_values_parsing import get_file_stats_column_from_attribute_kind

logger = get_shared_logger()


class AttributeCompareExpression(CompareExpression):

    def get_attribute_kind_from_string(self, session: Session, string_value: str) -> [str, dict]:
        attr_group_name = string_value.split('.')[1]
        attribute_group = Attribute_Template_Group.get_by_name_and_project(
            session = session,
            name = attr_group_name,
            project_id = self.project_id
        )

        if not attribute_group:
            # Strip underscores
            attr_group_name = attr_group_name.replace('_', ' ')
            attribute_group = Attribute_Template_Group.get_by_name_and_project(
                session = session,
                name = attr_group_name,
                project_id = self.project_id
            )
        if not attribute_group:
            error_string = f"Attribute Group {str(attr_group_name)} does not exists"
            logger.error(error_string)
            self.log['error']['attr_group_name'] = error_string
            return None, self.log
        return attribute_group.kind, self.log

    def build_expression_subquery(self, session) -> Query:

        attribute_kind, log = self.get_attribute_kind_from_string(
            session = session,
            string_value = self.query_op.query_entity.full_key
        )
        query_op: QueryElement = self.query_op
        scalar_op: QueryElement = self.scalar_op

        # Get Values from query elements
        raw_scalar_value = scalar_op.raw_value
        sql_filter = query_op.subquery
        sql_compare_operator = self.operator.operator_value
        file_stats_column = get_file_stats_column_from_attribute_kind(attribute_kind)
        if attribute_kind in ['radio', 'multiple_select', 'select', 'tree']:
            if self.compare_op_raw == 'in':
                try:
                    raw_scalar_value = list(raw_scalar_value)
                except:
                    self.log['error'] = f'Expecting an list value, not {raw_scalar_value}'
                    return
            else:
                try:
                    raw_scalar_value = int(raw_scalar_value)
                except:
                    self.log['error'] = f'Expecting an integer value, not {raw_scalar_value}'
                    return
        new_filter_subquery = sql_filter.filter(
            sql_compare_operator(file_stats_column, raw_scalar_value)
        ).subquery()
        self.subquery = new_filter_subquery
