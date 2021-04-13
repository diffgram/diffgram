# OPENCORE - ADD
from methods.regular.regular_api import logger
from methods.task.task_template.task_template_after_launch_strategies.task_template_after_launch_strategy import \
    TaskTemplateAfterLaunchStrategy
from shared.utils import job_dir_sync_utils


class StandardTaskTemplateAfterLaunchStrategy(TaskTemplateAfterLaunchStrategy):

    def execute_after_launch_strategy(self):
        """
            This strategy will attach files from sync directories and creates tasks in
            Diffgram for each of them.
        :return:
        """
        job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session=self.session,
            job=self.task_template,
            log=self.log
        )

        job_sync_manager.create_file_links_for_attached_dirs(create_tasks=True)
        # This removes the job from initial file sync queue.
        self.task_template.pending_initial_dir_sync = False
        self.session.add(self.task_template)
        logger.debug('StandardTaskTemplateAfterLaunchStrategy for Task Template ID: {} completed successfully.'.format(
            self.task_template.id))
