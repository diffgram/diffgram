from shared.shared_logger import get_shared_logger
import traceback

logger = get_shared_logger()

ACTION_RUNNERS_KIND_MAPPER = {}

try:
    from .ExportActionRunner import ExportActionRunner
    ACTION_RUNNERS_KIND_MAPPER[ExportActionRunner.kind] = ExportActionRunner
except:
    logger.error(traceback.format_exc())

try:
    from .TaskTemplateActionRunner import TaskTemplateActionRunner
    ACTION_RUNNERS_KIND_MAPPER[TaskTemplateActionRunner.kind] = TaskTemplateActionRunner
except:
    logger.error(traceback.format_exc())

try:
    from .AzureTextAnalyticsSentiment import AzureTextAnalyticsSentimentAction
    ACTION_RUNNERS_KIND_MAPPER[AzureTextAnalyticsSentimentAction.kind] = AzureTextAnalyticsSentimentAction
except:
    logger.error(traceback.format_exc())

try:
    from .DeepCheckImagePropertyOutliers import DeepcheckImagePropertyOutliers
    ACTION_RUNNERS_KIND_MAPPER[DeepcheckImagePropertyOutliers.kind] = DeepcheckImagePropertyOutliers
except Exception as e:
    logger.error(traceback.format_exc())

try:
    from .HuggingFaceZeroShot import HuggingFaceZeroShotAction
    ACTION_RUNNERS_KIND_MAPPER[HuggingFaceZeroShotAction.kind] = HuggingFaceZeroShotAction
except:
    logger.error(traceback.format_exc())

try:
    from .VertexTrainDatasetAction import VertexTrainDatasetAction
    ACTION_RUNNERS_KIND_MAPPER[VertexTrainDatasetAction.kind] = VertexTrainDatasetAction
except:
    logger.error(traceback.format_exc())

try:
    from .Webhook import WebhookAction
    ACTION_RUNNERS_KIND_MAPPER[WebhookAction.kind] = WebhookAction
except:
    logger.error(traceback.format_exc())