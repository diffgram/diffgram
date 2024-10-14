from action_runners.base.ActionRunner import ActionRunner  # Importing the base ActionRunner class
from shared.shared_logger import get_shared_logger  # Importing the shared logger
from shared.regular.regular_log import log_has_error  # Importing log_has_error function
from shared.export.export_create import create_new_export  # Importing create_new_export function
from shared.database.action.action import ActionKinds  # Importing ActionKinds enum
from shared.database.task.job.job import Job  # Importing Job class
from sqlalchemy.orm import Session  # Importing Session class
from action_runners.base.ActionTrigger import ActionTrigger  # Importing ActionTrigger class
from action_runners.base.ActionCondition import ActionCondition  # Importing ActionCondition class
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition  # Importing ActionCompleteCondition class

logger = get_shared_logger()  # Creating the logger instance

class ExportActionRunner(ActionRunner):
    """
    A class representing an action runner for JSON Export.
    Inherits from the base ActionRunner class.
    """
    public_name = 'JSON Export'  # The public name of the action runner
    description = 'Generate JSON Export'  # The description of the action runner
    icon = 'https://www.svgrepo.com/show/46774/export.svg'  # The icon URL of the action runner
    kind = 'export'  # The kind of the action runner
    trigger_data = ActionTrigger(  # The trigger data for the action runner
        default_event='task_completed', 
        event_list=["input_file_uploaded",
                    "task_completed", 
                    "action_completed", "time_trigger"]
    )
    precondition = ActionCondition(default_event='all_tasks_completed', event_list=["all_tasks_completed"])  # The precondition for the action runner
    completion_condition_data = ActionCompleteCondition(default_event='export_generate_success', event_list=["export_generate_success"])  # The completion condition data for the action runner

    def execute_pre_conditions(self, session: Session) -> bool:
        """
        Executes the pre-conditions for the action.
        :param session: The database session object.
        :return: True if pre-conditions are met, False otherwise.
        """
        event_name = self.action.precondition.get('event_name')
        if event_name is None:
            return True
        if event_name == 'all_tasks_completed':
            prev_action = self.action.get_previous_action(session=session)
            if prev_action is None:
                logger.warning(f'Warning no previous action for action ID {self.action.id}')
                return True
            if prev_action.kind == ActionKinds.create_task.value:
                task_template_id = self.action.config_data.get('task_template_id')
                task_template = Job.get_by_id(session=session, job_id=task_template_id)
                if task_template.status == 'complete':
                    logger.info('Pre condition pass. Task template is completed.')
                    return True
                else:
                    logger.warning(
                        f'Pre condition failed. Task template not completed. Status is: {task_template.status}')
                    return False
            else:
                logger.warning(
                    f'Previous Action kind: {prev_action.kind} not applicable to precondition. Stopping execution.')
                return False
        return False

    def execute_action(self, session: Session) -> bool:
        """
        Executes the action.
        :param session: The database session object.
        :return: True if action is executed successfully, False otherwise.
        """
        logger.debug('Starting export generation action...')
        source = self.action.config_data.get('source')
        task_template_id = self.action.config_data.get('task_template_id')
        directory_id = self.action.config_data.get('directory_id')
        task_id = self.action.config_data.get('task_id')
        kind = self.action.config_data.get('kind')
        ann_is_complete = self.action.config_data.get('ann_is_complete')
        logger.debug(f'Action config is {self.action.config_data}')
        project = self.action.project
        member_id = self.event_data.get('member_id')
        export_data, log = create_new_export(
            session=session,
            project=project,
            source=source,
            task_id=task_id,
            job_id=task_template_id,
            directory_id=directory_id,
            file_comparison_mode=None,
            kind=kind,
            ann_is_complete=ann_is_complete,
            wait_for_export_generation=True,
            member_id=member_id
        )
        if log_has_error(log):
            self.declare_action_failed(session)
            return False
        logger.info(f'Export: generated successfully.')
        return True
