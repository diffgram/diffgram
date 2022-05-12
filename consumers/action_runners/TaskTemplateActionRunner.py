from consumers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
logger = get_shared_logger()


class TaskTemplateActionRunner(ActionRunner):

    def run(self):
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