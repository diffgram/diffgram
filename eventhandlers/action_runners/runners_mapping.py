from shared.regular.regular_api import *
from action_runners.base.ActionRunner import ActionRunner
from shared.database.action.action import Action
from shared.shared_logger import get_shared_logger
from action_runners.ExportActionRunner import ExportActionRunner
from action_runners.TaskTemplateActionRunner import TaskTemplateActionRunner

ACTION_RUNNERS_KIND_MAPPER = {
    'create_task': TaskTemplateActionRunner,
    'export': ExportActionRunner
}

try:
    from action_runners.AzureTextAnalyticsSentiment import AzureTextAnalyticsSentimentAction
    ACTION_RUNNERS_KIND_MAPPER["AzureTextAnalyticsSentimentAction"] = AzureTextAnalyticsSentimentAction
except:
    print("AzureTextAnalyticsSentimentAction is not avalible on your installation")

try:
    from action_runners.DeepCheckImagePropertyOutliers import DeepcheckImagePropertyOutliers
    ACTION_RUNNERS_KIND_MAPPER["deep_checks__image_properties_outliers"] = DeepcheckImagePropertyOutliers
except:
    print("deep_checks__image_properties_outliers is not avalible on your installation")

logger = get_shared_logger()

def register_all():
    with sessionMaker.session_scope() as session:
        for key, value in ACTION_RUNNERS_KIND_MAPPER.items():
            logger.info(f'Registering: {key}')
            runner = value(action = None, event_data = None)
            runner.register(session = session)


def get_runner(action: Action, event_data) -> ActionRunner:
    """
        Returns actions runner object based on action kind.
    :return:
    """

    class_name = ACTION_RUNNERS_KIND_MAPPER[action.kind]

    runner = class_name(action = action, event_data = event_data)
    return runner
