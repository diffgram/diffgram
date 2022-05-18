from consumers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.regular.regular_log import log_has_error
from shared.export.export_create import create_new_export
from shared.database.action.action import ActionTriggerEventTypes
from shared.database.task.job.job import Job
logger = get_shared_logger()


class ExportActionRunner(ActionRunner):
    def execute_pre_conditions(self, session) -> bool:
        event_name = self.action.condition_data.get('event_name')

        print('pre conditions', event_name)
        if event_name is None:
            return True
        print('pre conditions', event_name)
        if event_name == 'all_tasks_completed':
            prev_action = self.action.get_previous_action(session = session)
            if prev_action is None:
                logger.warning(f'Warning no previous action for action ID {self.action.id}')
            if prev_action.kind == ActionTriggerEventTypes.task_created.value:
                task_template_id = self.action.config_data.get('task_template_id')
                task_template = Job.get_by_id(session = session, job_id = task_template_id)
                if task_template.status == 'complete':
                    return True
                else:
                    return False
        return False

    def execute_action(self, session) -> bool:
        """
            Creates a task from the given file_id in the given task template ID.
            :return: True if access was succesfull false in other case.
       """
        source = self.action.config_data.get('source')
        task_template_id = self.action.config_data.get('task_template_id')
        directory_id = self.action.config_data.get('directory_id')
        task_id = self.action.config_data.get('task_id')
        kind = self.action.config_data.get('kind')
        ann_is_complete = self.action.config_data.get('ann_is_complete')

        project = self.action.project
        export_data, log = create_new_export(
            session = session,
            project = project,
            source = source,
            task_id = task_id,
            job_id = task_template_id,
            directory_id = directory_id,
            file_comparison_mode = None,
            kind = kind,
            ann_is_complete = ann_is_complete,
            wait_for_export_generation = True
        )
        if log_has_error(log):
            self.declare_action_failed(session)
            return True
        logger.info(f'Export Action Executed Export ID: {export_data["export"]["id"]}')
