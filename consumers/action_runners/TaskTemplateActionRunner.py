from consumers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
logger = get_shared_logger()


class TaskTemplateActionRunner(ActionRunner):
    def execute_pre_conditions(self, session):
        return

    def run(self):
        """
            Creates a task from the given file_id in the given task template ID.
        :return:
        """
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
            job_sync_manager.create_task_from_file(file)