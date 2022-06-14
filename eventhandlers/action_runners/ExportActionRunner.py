from action_runners.base.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.regular.regular_log import log_has_error
from shared.export.export_create import create_new_export
from shared.database.action.action import ActionKinds
from shared.database.task.job.job import Job
from shared.database.action.action_template import Action_Template
from sqlalchemy.orm import Session
from shared.database.action.action_run import ActionRun

logger = get_shared_logger()


class ExportActionRunner(ActionRunner):
    def execute_pre_conditions(self, session: Session, action_run: ActionRun) -> bool:
        event_name = self.action.condition_data.get('event_name')
        if event_name is None:
            return True
        if event_name == 'all_tasks_completed':
            prev_action = self.action.get_previous_action(session = session)
            if prev_action is None:
                logger.warning(f'Warning no previous action for action ID {self.action.id}')
                return
            if prev_action.kind == ActionKinds.create_task.value:
                task_template_id = self.action.config_data.get('task_template_id')
                task_template = Job.get_by_id(session = session, job_id = task_template_id)
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

    def execute_action(self, session: Session, action_run: ActionRun) -> bool:
        """
            Creates a task from the given file_id in the given task template ID.
            :return: True if access was succesfull false in other case.
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
            session = session,
            project = project,
            source = source,
            task_id = task_id,
            job_id = task_template_id,
            directory_id = directory_id,
            file_comparison_mode = None,
            kind = kind,
            ann_is_complete = ann_is_complete,
            wait_for_export_generation = True,
            member_id = member_id
        )
        if log_has_error(log):
            self.declare_action_failed(session)
            return True
        logger.info(f'Export: generated successfully.')

    def register(self, session):

        Action_Template.register(
            session = session,
            public_name = 'JSON Export',
            description = 'Generate JSON Export',
            icon = 'https://www.svgrepo.com/show/46774/export.svg',
            kind = 'export',
            category = None,
            trigger_data = {'trigger_event_name': 'task_completed'},
            condition_data = {'event_name': 'all_tasks_completed'},
            completion_condition_data = {'event_name': 'export_generate_success'},
        )
