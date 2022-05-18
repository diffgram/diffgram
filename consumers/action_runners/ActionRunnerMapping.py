from consumers.action_runners.ExportActionRunner import ExportActionRunner
from consumers.action_runners.TaskTemplateActionRunner import TaskTemplateActionRunner

ACTION_RUNNERS_KIND_MAPPER = {
    'create_task': TaskTemplateActionRunner,
    'export': ExportActionRunner,
}
