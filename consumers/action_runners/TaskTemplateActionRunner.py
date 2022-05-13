from consumers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from shared.utils.sync_events_manager import SyncEventManager

logger = get_shared_logger()


class TaskTemplateActionRunner(ActionRunner):
    def execute_pre_conditions(self, session):
        return

    def run(self):
        """
            Creates a task from the given file_id in the given task template ID.
        :return:
        """
        self.event_data['directory_id']
        with session_scope() as session:
            if not self.action.config_data:
                logger.warning(f'Action has no config data. Stopping execution')
                return
            tt_id = self.action.config_data.get('task_template_id')
            if not tt_id:
                logger.warning(f'Action has no task_template_id Stopping execution')
                return

            task_template = Job.get_by_id(session, job_id = tt_id)

            file_id = self.event_data['file_id']
            if not file_id:
                logger.warning(f'Action has no file_id Stopping execution')
                return

            file = File.get_by_id(session, file_id = file_id)
            job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
                session = self.session,
                job = task_template,
                log = self.log
            )
            sync_event_manager = SyncEventManager.create_sync_event_and_manager(
                session = self.session,
                dataset_source_id = directory_for_job_sync,
                dataset_destination = None,
                description = 'Sync file from dataset {} to job {} and create task'.format(
                    directory_for_job_sync.nickname,
                    job.name
                ),
                file = file,
                job = job,
                input_id = file.input_id,
                project = job.project,
                event_effect_type = 'create_task',
                event_trigger_type = 'file_added',
                status = 'init',
                member_created = member
            )
            job_sync_manager.create_task_from_file(
                file = file,
                incoming_directory = dir,
                job = task_template,
                create_tasks = True,
                sync_event_manager = sync_event_manager
            )
