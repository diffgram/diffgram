from shared.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from shared.utils.sync_events_manager import SyncEventManager
from shared.database.source_control.working_dir import WorkingDir
from shared.database.auth.member import Member
from shared.regular.regular_log import log_has_error
from shared.export.export_create import create_new_export

logger = get_shared_logger()


class ExportActionRunner(ActionRunner):
    def execute_pre_conditions(self, session):
        return

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
