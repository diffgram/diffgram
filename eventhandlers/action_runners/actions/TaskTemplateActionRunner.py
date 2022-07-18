from action_runners.base.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from shared.utils.sync_events_manager import SyncEventManager
from shared.database.source_control.working_dir import WorkingDir
from shared.database.auth.member import Member
from sqlalchemy.orm.session import Session
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition

logger = get_shared_logger()


class TaskTemplateActionRunner(ActionRunner):
    public_name = 'Human Labeling Tasks'
    description = 'Add tasks to a task template'
    icon = 'https://www.svgrepo.com/show/376121/list-task.svg'
    kind = 'TaskTemplateActionRunner'
    trigger_data = ActionTrigger(default_event = 'input_file_uploaded', event_list = ["input_file_uploaded", "action_completed"])
    precondition = ActionCondition(default_event = None, event_list = [])
    completion_condition_data = ActionCompleteCondition(default_event = 'task_completed', event_list = ["task_completed"])

    def execute_pre_conditions(self, session: Session) -> bool:
        if self.action.trigger_data.get('event_name') == 'action_completed':
            result = self.event_data.get('extra_metadata', {}).get('applied_option_id')
            output_labels = self.action.precondition.get('output_labels')
            if not output_labels or len(output_labels) == 0:
                return True
            condition_is_satisfied = any(label['id'] == result for label in output_labels)
            return condition_is_satisfied
        return True

    def execute_action(self, session: Session):
        """
                   Creates a task from the given file_id in the given task template ID.
               :return:
               """
        dir_id = self.event_data.get('directory_id')
        member_id = self.event_data.get('member_id')
        logger.info(f'Attempting to create task from {dir_id}')
        if self.action.trigger_data.get('event_name') == 'action_completed':
            dir_id = self.event_data.get('extra_metadata', {}).get('directory_id')
        if dir_id is None:
            logger.warning(f'Cannot add task, provide directory_id in event data.')
            return

        if not self.action.config_data:
            logger.warning(f'Action has no config data. Stopping execution')
            return
        task_template_id = self.action.config_data.get('task_template_id')
        logger.info(f'Task template {task_template_id}')
        if not task_template_id:
            logger.warning(f'Action has no task_template_id Stopping execution')
            return

        task_template = Job.get_by_id(session, job_id = task_template_id)

        file_id = self.event_data.get('file_id')
        if self.action.trigger_data.get('event_name') == 'action_completed':
            file_id = self.event_data.get('extra_metadata').get('file_id')

        if not file_id:
            logger.warning(f'Action has no file_id Stopping execution')
            return

        file = File.get_by_id(session, file_id = file_id)
        job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session = session,
            job = task_template,
            log = self.log
        )
        directory = WorkingDir.get_by_id(session = session, directory_id = dir_id)
        member = Member.get_by_id(session = session, member_id = member_id)
        sync_event_manager = SyncEventManager.create_sync_event_and_manager(
            session = session,
            dataset_source_id = directory,
            dataset_destination = None,
            description = 'Sync file from dataset {} to job {} and create task'.format(
                directory.nickname,
                task_template.name
            ),
            file = file,
            job = task_template,
            input_id = file.input_id,
            project = task_template.project,
            event_effect_type = 'create_task',
            event_trigger_type = 'file_added',
            status = 'init',
            member_created = member
        )

        task, log = job_sync_manager.add_file_into_job(
            file = file,
            incoming_directory = directory,
            job = task_template,
            create_tasks = True,
            sync_event_manager = sync_event_manager
        )
        self.log = log
        task_template.update_file_count_statistic(session = session)
        task_template.refresh_stat_count_tasks(session = session)
        return {
            'file_id': file.id,
            'task_id': task.id if task is not None else None,
            'task_template_id': task_template_id
        }
