from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from sqlalchemy.orm import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.file_stats import FileStats
from shared.shared_logger import get_shared_logger
from lark import Token

logger = get_shared_logger()


class AttributeQueryElement(QueryElement):
    top_level_key = "attribute"

    def __init__(self):
        pass

    def create_from_token(self, session: Session, project_id: int, log: dict, token: Token) -> ['AttributeQueryElement',
                                                                                                dict]:

        attr_group_name = self.top_level_key

        attribute_group = Attribute_Template_Group.get_by_name_and_project(
            session = session,
            name = attr_group_name,
            project_id = project_id
        )

        if not attribute_group:
            # Strip underscores
            attr_group_name = attr_group_name.replace('_', ' ')
            attribute_group = Attribute_Template_Group.get_by_name_and_project(
                session = session,
                name = attr_group_name,
                project_id = project_id
            )
        if not attribute_group:
            error_string = f"Attribute Group {str(attr_group_name)} does not exists"
            logger.error(error_string)
            log['error']['attr_group_name'] = error_string
            return None, log
        attr_group_query = (session.query(FileStats.file_id).filter(
            FileStats.attribute_template_group_id == attribute_group.id
        ))
        result = AttributeQueryElement(subquery = attr_group_query)
        return result, log

    @staticmethod
    def get_attribute_kind_from_string(session: Session, log: dict, project_id: int, string_value: str) -> [str, dict]:
        attr_group_name = string_value.split('.')[1]
        attribute_group = Attribute_Template_Group.get_by_name_and_project(
            session = session,
            name = attr_group_name,
            project_id = project_id
        )

        if not attribute_group:
            # Strip underscores
            attr_group_name = attr_group_name.replace('_', ' ')
            attribute_group = Attribute_Template_Group.get_by_name_and_project(
                session = session,
                name = attr_group_name,
                project_id = project_id
            )
        if not attribute_group:
            error_string = f"Attribute Group {str(attr_group_name)} does not exists"
            logger.error(error_string)
            log['error']['attr_group_name'] = error_string
            return None, log
        return attribute_group.kind, log

    @staticmethod
    def build_query(session: Session, log: dict, project_id: int, value_1: any, value_2: any,
                    compare_op_token: Token) -> ['CompareExpression', dict]:

        attribute_kind, log = CompareExpression.get_attribute_kind_from_string(
            session = session,
            log = log,
            project_id = project_id,
            string_value = scalar_op
        )
        sql_compare_operator = CompareOperator.create_compare_operator_from_token(compare_op_token)
        file_stats_column = get_file_stats_column_from_attribute_kind(attribute_kind)

        if attribute_kind in ['radio', 'multiple_select', 'select', 'tree']:
            scalar_op = int(scalar_op)

        self.subquery = query_op.filter(sql_compare_operator(file_stats_column, scalar_op)).subquery()
        return self.subquery
