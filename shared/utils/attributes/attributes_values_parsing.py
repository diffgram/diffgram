import datetime

from sqlalchemy.orm.session import Session
from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


def get_attribute_value(session: Session, attr_id: int, attribute_value: any) -> [any, str]:
    attribute_group = Attribute_Template_Group.get_by_id(
        session = session,
        id = attr_id
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

    elif attribute_value.kind == 'date':
        # For date attributes we return a date time.
        value = datetime.datetime.strptime(attribute_value, "%Y-%m-%d")
    elif attribute_value.kind == 'date':
        # For date attributes we return a date time.
        value = datetime.datetime.strptime(attribute_value, "%Y-%m-%d")


    return value, attribute_group.kind