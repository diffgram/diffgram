import datetime

from sqlalchemy.orm.session import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.shared_logger import get_shared_logger
import time
from sqlalchemy import Column
from shared.database.project import Project
from time import mktime

logger = get_shared_logger()


def get_file_stats_column_from_attribute_kind(attr_kind: str) -> Column or None:
    from shared.database.source_control.file_stats import FileStats
    val = None
    if attr_kind == 'tree':
        val = FileStats.attribute_template_id

    elif attr_kind == 'date':
        val = FileStats.attribute_value_selected_date
    elif attr_kind == 'time':
        val = FileStats.attribute_value_selected_time
    elif attr_kind == 'slider':
        val = FileStats.attribute_value_number
    elif attr_kind == 'radio':
        val = FileStats.attribute_template_id
    elif attr_kind == 'multiple_select':
        val = FileStats.attribute_template_id
    elif attr_kind == 'text':
        val = FileStats.attribute_value_text
    elif attr_kind == 'select':
        val = FileStats.attribute_template_id
    else:
        logger.error(f'Invalid attribute kind {attr_kind}')
        return None
    return val


def get_attribute_value(session: Session, attr_id: int, attribute_value: any, project: Project) -> [any, str]:
    attribute_group = Attribute_Template_Group.get_by_id(
        session = session,
        id = attr_id,
        project_id = project.id
    )
    value = None
    if attribute_group is None:
        logger.error(f'Attribute Group does not exists: {attr_id}')
        return None, None

    if attribute_group.kind == 'tree':
        # For tree attributes we will return a list with the ID of all the selected attribute templates.
        selected_dict = attribute_value
        value = []
        for key, val in selected_dict.items():
            if selected_dict[key].get('selected'):
                value.append(key)

    elif attribute_group.kind == 'date':
        # For date attributes we return a date time.
        if attribute_value is None:
            return None, None
        value = datetime.datetime.strptime(attribute_value, "%Y-%m-%d")
    elif attribute_group.kind == 'time':
        # For time attributes we return a time object.
        if attribute_value is None:
            return None, None
        value = time.strptime(attribute_value, "%H:%M")
        value = datetime.datetime.fromtimestamp(mktime(value))
    elif attribute_group.kind == 'slider':
        value = int(attribute_value)
    elif attribute_group.kind == 'radio':
        if type(attribute_value) != dict:
            return None, None
        value = int(attribute_value['id'])
    elif attribute_group.kind == 'multiple_select':
        value = []
        if not isinstance(attribute_value, list):
            attribute_value = [attribute_value]
        for option in attribute_value:
            if option is None:
                continue
            id = option.get('id')
            if id:
                value.append(int(id))
    elif attribute_group.kind == 'text':
        value = str(attribute_value)
    elif attribute_group.kind == 'select':
        if type(attribute_value) != dict:
            return None, None
        value = attribute_value.get('id')
        if value is not None:
            value = int(value)
    return value, attribute_group.kind
