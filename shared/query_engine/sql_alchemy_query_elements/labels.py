from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from sqlalchemy.orm import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.source_control.file_stats import FileStats
from shared.shared_logger import get_shared_logger
from lark import Token
from sqlalchemy.sql import Selectable
from shared.database.source_control.file import File

logger = get_shared_logger()


class LabelsQueryElement(QueryElement):
    top_level_key = "attribute"

    def __init__(self):
        pass

    def build_query(self, session: Session, token: Token) -> Selectable:

        label_name = token.value.split('.')[1]

        label_file = File.get_by_label_name(session = session,
                                            label_name = label_name,
                                            project_id = self.project_id)
        if not label_file:
            # Strip underscores
            label_name = label_name.replace('_', ' ')
            label_file = File.get_by_label_name(session = session,
                                                label_name = label_name,
                                                project_id = self.project_id)
        if not label_file:
            error_string = f"Label {str(label_name)} does not exists"
            logger.error(error_string)
            self.log['error']['label_name'] = error_string
            return None
        instance_count_query = session.query(FileStats.file_id).filter(
            FileStats.label_file_id == label_file.id
        )
        self.subquery = instance_count_query
        return instance_count_query
