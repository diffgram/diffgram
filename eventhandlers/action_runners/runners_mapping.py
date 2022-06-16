from shared.regular.regular_api import *
from action_runners.ExportActionRunner import ExportActionRunner
from action_runners.TaskTemplateActionRunner import TaskTemplateActionRunner
from action_runners.AzureTextAnalyticsSentiment import AzureTextAnalyticsSentimentAction
from action_runners.DeepCheckImagePropertyOutliers import DeepcheckImagePropertyOutliers
from action_runners.base.ActionRunner import ActionRunner
from shared.database.action.action import Action
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()
ACTION_RUNNERS_KIND_MAPPER = {
    'create_task': TaskTemplateActionRunner,
    'export': ExportActionRunner,
    'AzureTextAnalyticsSentimentAction': AzureTextAnalyticsSentimentAction,
    'deep_checks__image_properties_outliers': DeepcheckImagePropertyOutliers
}


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
