from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from sqlalchemy.orm import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.file_stats import FileStats
from shared.shared_logger import get_shared_logger
from lark import Token
from sqlalchemy.sql import Selectable

logger = get_shared_logger()


class AttributeQueryElement(QueryElement):
    top_level_key = "attribute"

    def __init__(self):
        pass

    def build_query(self, session: Session, token: Token) -> Selectable:

        attr_group_name = self.query_entity.full_key.split('.')[1]

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
            error_string = f"Attribute Group '{str(attr_group_name)}' does not exists"
            logger.error(error_string)
            self.log['error']['attr_group_name'] = error_string
            return
        attr_group_query = session.query(FileStats.file_id).filter(
            FileStats.attribute_template_group_id == attribute_group.id
        )
        self.subquery = attr_group_query
        return self.subquery