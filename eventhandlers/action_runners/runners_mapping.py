from shared.regular.regular_api import *
from action_runners.ExportActionRunner import ExportActionRunner
from action_runners.TaskTemplateActionRunner import TaskTemplateActionRunner
from action_runners.AzureTextAnalyticsSentiment import AzureTextAnalyticsSentimentAction
from action_runners.ActionRunner import ActionRunner
from shared.database.action.action import Action

ACTION_RUNNERS_KIND_MAPPER = {
    'create_task': TaskTemplateActionRunner,
    'export': ExportActionRunner,
    'AzureTextAnalyticsSentimentAction' : AzureTextAnalyticsSentimentAction
}



def register_all():
    with sessionMaker.session_scope() as session:
        for key, value in ACTION_RUNNERS_KIND_MAPPER.items():
            value.register(session=session)

register_all()

def get_runner(action: Action, event_data) -> ActionRunner:
    """
        Returns actions runner object based on action kind.
    :return:
    """

    class_name = ACTION_RUNNERS_KIND_MAPPER[action.kind]

    runner = class_name(action = action, event_data = event_data)
    return runner
