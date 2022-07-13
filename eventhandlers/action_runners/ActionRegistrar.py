from shared.database.action.action_template import Action_Template
from shared.regular.regular_api import *
from action_runners.base.ActionRunner import ActionRunner
from shared.database.action.action import Action
from shared.shared_logger import get_shared_logger
from .actions import ACTION_RUNNERS_KIND_MAPPER

logger = get_shared_logger()

def register_all():
    with sessionMaker.session_scope() as session:
        avalible_actions = [action.kind for action in Action_Template.list_avalible_kinds(session)]
        for key, value in ACTION_RUNNERS_KIND_MAPPER.items():
            if value.kind in avalible_actions:
                avalible_actions.remove(value.kind)
                logger.info(f'Updating: {key}')
                runner = value(action = None, event_data = None)
                runner.update(session = session)
            else:
                logger.info(f'Registering: {key}')
                runner = value(action = None, event_data = None)
                runner.register(session = session)

        for action in avalible_actions:
            Action_Template.unregister_by_kind(session, action)


def get_runner(action: Action, event_data) -> ActionRunner:
    """
        Returns actions runner object based on action kind.
    :return:
    """

    class_name = ACTION_RUNNERS_KIND_MAPPER[action.kind]

    runner = class_name(action = action, event_data = event_data)
    return runner
