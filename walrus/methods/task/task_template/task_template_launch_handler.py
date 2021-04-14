from methods.regular.regular_api import *
import threading

from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.task.job.job_launch import JobLaunchQueue, JobLaunch
from methods.regular.regular_api import logger
from methods.task.task_template.task_template_after_launch_strategies.labelbox_task_template_after_launch_strategy import \
    LabelboxTaskTemplateAfterLaunchStrategy
from methods.task.task_template.task_template_after_launch_strategies.standard_task_template_after_launch_strategy import \
    StandardTaskTemplateAfterLaunchStrategy
from methods.task.task_template.task_template_after_launch_strategies.datasaur_task_template_after_launch_strategy import \
    DatasaurTaskTemplateAfterLaunchStrategy
from methods.task.task_template.task_template_after_launch_strategies.scale_ai_task_template_after_launch_strategy import \
    ScaleAITaskTemplateAfterLaunchStrategy
from shared.utils.task import task_new
from shared.settings import settings
from shared.regular import regular_log
from shared.utils import job_dir_sync_utils
from shared.utils.job_launch_utils import task_template_label_attach
from tenacity import retry, stop_after_attempt
import traceback


def task_template_launch_core(session,
                              job):
    """

        This function is in charge of attaching the labels to the job, setting status to active
        and then creating the root tasks for each of the files attached to the job.
    """
    if not job:
        return False
    # TODO other pre checks (ie that guide is attached,
    # has a bid, files, etc.

    # check Status is "launchable" ie in draft

    # Update job status
    log = regular_log.default()
    # CAUTION using default directory for project which may not be right
    result = task_template_label_attach(session=session,
                                        task_template=job,
                                        project_directory=job.project.directory_default,
                                        )

    # QUESTION Do we only need to create tasks for "normal work things"?
    # ie for exams it gets done as part of the process
    # QUESTION are these only relevant for normal work? not exam?

    if job.type == "Normal":
        task_template_new_normal(session=session,
                                 task_template=job)

    if job.type == "Exam":
        task_template_new_exam(session=session,
                               task_template=job)

    # Add job to all attached directories
    job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
        session=session,
        job=job,
        log=log
    )

    assert job is not None

    session.add(job)

    return job


def task_template_new_normal(session, task_template):
    """

    """

    # job is in session so no need to return it

    # TODO: analyze if this code is needed.
    result = task_new.provision_root_tasks(
        session=session,
        job=task_template)

    session.add(task_template)
    task_template.status = "active"


def task_template_new_exam(session, task_template):
    """
    We don't create tasks here, since a person starting a new Exam
    will create a new job and new tasks
    """

    session.add(task_template)
    task_template.status = "active"


def on_launch_error_retry(retry_state):
    if retry_state.outcome:
        logger.error('Error Launching job. Retrying... {}/3'.format(retry_state.attempt_number))


class TaskTemplateLauncherThread:

    def __init__(self,
                 run_once=True,
                 thread_sleep_time_min=0,
                 thread_sleep_time_max=0,):

        if run_once is True:
            self.thread = threading.Thread(
                target=self.check_if_jobs_to_launch)
        else:
            self.thread_sleep_time_min = thread_sleep_time_min
            self.thread_sleep_time_max = thread_sleep_time_max

            self.thread = threading.Thread(target=self.start_queue_check_loop)

        if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
            self.thread.daemon = True  # Allow hot reload to work
            self.thread.start()

    def start_queue_check_loop(self):
        """

        """
        regular_methods.loop_forever_with_random_load_balancing(
            log_start_message='Starting JobLaunch Queue handler... ',
            log_heartbeat_message='[Job Launch Queue heartbeat]',
            function_call=self.check_if_jobs_to_launch,
            function_args={},
            thread_sleep_time_min=self.thread_sleep_time_min,
            thread_sleep_time_max=self.thread_sleep_time_max,
            logger=logger
            )


    @retry(stop=stop_after_attempt(3), reraise=True, after=on_launch_error_retry)
    def launch_job(self, session, task_template_queue_element):
        task_template = task_template_queue_element.job_launch.job
        task_template_launch_core(session=session, job=task_template)

        after_launch_control = AfterLaunchControl(
            session=session,
            task_template=task_template)

        after_launch_control.main()
        task_template_queue_element.job_launch.time_completed = datetime.datetime.utcnow()
        task_template_queue_element.job_launch.status = 'completed'
        task_template_queue_element.job_launch.job_launch_info = 'Job Launched Successfully.'
        session.add(task_template_queue_element.job_launch)
        # If no errors, remove the queue element
        session.query(JobLaunchQueue).filter(JobLaunchQueue.id == task_template_queue_element.id).delete()

    def check_if_jobs_to_launch(self):
        """
            Gets the first element of the queue
        """
        task_template_queue_element_id = None
        try:
            with sessionMaker.session_scope_threaded() as session:

                # Main assumptions for pulling 1 at a time
                # 1) On deployments, each instance has multiple workers that run this. In that context, each worker can
                # grab the next element.
                # 2) Each task template launch *process* itself is 'heavy' we don't want to block every 2nd, 3rd launch on 1st one.
                #   eg we assume the ratio of task template to files(tasks) is something like 10+:1 (and often more like hundreds:1))
                # 3) Where as JobLaunchQueue query is lightweight, it's fine to run it relatively often

                task_template_queue_element = session.query(JobLaunchQueue).with_for_update(skip_locked=True).first()
                task_template_queue_element_id = int(task_template_queue_element.id)
                # Can use sort in sql if needed here
                if task_template_queue_element:
                        self.launch_job(session, task_template_queue_element)
        except Exception as e:
            if task_template_queue_element_id:
                with sessionMaker.session_scope_threaded() as session:
                    task_template_queue_element = session.query(JobLaunchQueue).filter(
                        JobLaunchQueue.id == task_template_queue_element_id
                    ).first()
                    if not task_template_queue_element:
                        return
                    job_launch = JobLaunch.get_by_id(session=session, job_launch_id=task_template_queue_element.job_launch_id)
                    job = Job.get_by_id(session, job_id=job_launch.job_id)
                    logger.critical('Error launching Job {}'.format(job.id))
                    task_template_queue_element.job_launch.status = 'failed'
                    # TODO, we can remove this when we have a better UI visualization for JobLaunch
                    task_template_queue_element.job_launch.job.status = 'failed'
                    task_template_queue_element.job_launch.job_launch_info = str(e)
                    logger.error(traceback.format_exc())
                    session.add(task_template_queue_element.job_launch)
                    logger.info('Deleting queue element'.format(task_template_queue_element.id))
                    session.query(JobLaunchQueue).filter(JobLaunchQueue.id == task_template_queue_element.id).delete()


class AfterLaunchControl:

    def __init__(
            self,
            session,
            task_template):

        self.session = session
        self.task_template = task_template
        self.log = regular_log.default()
        self.strategy = None

    def main(self):
        # We will not launch on bacgrkound now, we will just attach files from sync directories.
        self.strategy = self.determine_task_template_post_launch_strategy()
        self.strategy.execute_after_launch_strategy()

    def determine_task_template_post_launch_strategy(self):
        """
            This function will be routing to the appropriate launching algorithm depending on
            the task template configurations. For example, if an external interface was selected,
            the launch strategy will be different than if the standard Diffgram interface.
        :return:
        """
        logger.debug('Determining post launch strategy...')
        # We default to standard launch strategy.
        strategy = StandardTaskTemplateAfterLaunchStrategy(
            session=self.session,
            task_template=self.task_template,
            log=self.log
        )
        logger.debug('interface_connection is {}'.format(
            self.task_template.interface_connection))
        if self.task_template.interface_connection:
            interface_connection = self.task_template.interface_connection
            logger.debug('integration name is {}'.format(interface_connection.integration_name))
            # If task template has an integration with labelbox. Change the after launch strategy.
            if interface_connection.integration_name == 'labelbox':
                strategy = LabelboxTaskTemplateAfterLaunchStrategy(
                    session=self.session,
                    task_template=self.task_template,
                    log=self.log
                )
            if interface_connection.integration_name == 'datasaur':
                strategy = DatasaurTaskTemplateAfterLaunchStrategy(
                    session=self.session,
                    task_template=self.task_template,
                    log=self.log
                )
            if interface_connection.integration_name == 'scale_ai':
                strategy = ScaleAITaskTemplateAfterLaunchStrategy(
                    session=self.session,
                    task_template=self.task_template,
                    log=self.log
                )
        return strategy
