from methods.regular.regular_api import *
import random
import threading
import time
from shared.settings import settings
from tenacity import retry, stop_after_attempt
import traceback
from shared.database.sync_events.sync_action_queue import SyncActionsQueue
from shared.helpers import sessionMaker
from shared.utils.task import task_file_observers
from shared.regular import regular_log
from shared.utils.sync_events_manager import SyncEventManager
from shared.utils import job_dir_sync_utils


def on_launch_error_retry(retry_state):
    if retry_state.outcome:
        logger.error(f"Error on Sync execution. Retrying... {retry_state.attempt_number}/3")


class SyncActionsHandlerThread:

    def __init__(self,
                 thread_sleep_time_min = settings.SYNC_ACTIONS_THREAD_SLEEP_TIME_MIN,
                 thread_sleep_time_max = settings.SYNC_ACTIONS_THREAD_SLEEP_TIME_MAX,
                 run_once = True):

        if run_once is True:
            self.thread = threading.Thread(
                target = self.check_for_new_sync_actions)
        else:
            self.thread_sleep_time_min = thread_sleep_time_min
            self.thread_sleep_time_max = thread_sleep_time_max
            self.thread = threading.Thread(target = self.start_queue_check_loop)
        if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
            self.thread.daemon = True  # Allow hot reload to work
            self.thread.start()

    def start_queue_check_loop(self):
        """

        """
        regular_methods.loop_forever_with_random_load_balancing(
            log_start_message = 'Starting SyncActionsHandlerThread Queue handler... ',
            log_heartbeat_message = '[SyncActions Queue heartbeat]',
            function_call = self.check_for_new_sync_actions,
            function_args = {},
            thread_sleep_time_min = self.thread_sleep_time_min,
            thread_sleep_time_max = self.thread_sleep_time_max,
            logger = logger
        )

    def process_sync_actions(self, session, sync_action):
        """
            Executes sync action depending on the type of action
        :param session:
        :param sync_action:
        :return:
        """
        log = regular_log.default()
        sync_event = sync_action.sync_event
        sync_events_manager = SyncEventManager(session = session, sync_event = sync_event)
        logger.debug('Processing new sync event.')
        if sync_event.event_trigger_type == 'task_completed':
            completed_task = sync_event.completed_task
            job_observable = task_file_observers.JobObservable(session = session,
                                                               log = log,
                                                               job = completed_task.job,
                                                               task = completed_task,
                                                               sync_events_manager = sync_events_manager)
            job_observable.notify_all_observers(defer = False)
        elif sync_event.event_trigger_type == 'file_operation':
            logger.debug('Processing file_operation sync event.')
            destination_directory = sync_event.dataset_destination
            source_directory = None
            file = sync_event.file
            if sync_event.event_effect_type in ['file_copy', 'file_move']:
                logger.debug('Processing file_copy sync event.')
                if sync_event.event_effect_type == 'file_copy':
                    # we need to provide the source dir for validation of incoming dir.
                    source_directory = sync_event.dataset_source
                    file = sync_event.new_file_copy

                job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
                    session = session,
                    log = log,
                    directory = destination_directory,
                )
                # we need to provide the source dir, so validation of incoming
                # directory does not fail when checking the directory the file is coming from.
                logger.debug('Syncing file on jobs...')
                job_dir_sync_manager.add_file_to_all_jobs(
                    file = file,
                    source_dir = source_directory,
                    create_tasks = True,

                )
            else:
                logger.info(f"{sync_event.event_effect_type} event effect not supported for processing.")
        else:
            logger.info(f"{sync_event.event_trigger_type} event trigger not supported for processing.")

    def check_for_new_sync_actions(self):
        """
            Gets the first element of the queue
        """
        with sessionMaker.session_scope_threaded() as session:

            sync_action = session.query(SyncActionsQueue).with_for_update(skip_locked = True).first()
            # Can use sort in sql if needed here
            sync_action_id = None
            if sync_action:
                sync_action_id = int(sync_action.id)
            try:
                if sync_action:
                    try:
                        self.process_sync_actions(session, sync_action)
                        session.query(SyncActionsQueue).filter(SyncActionsQueue.id == sync_action.id).delete()
                    except Exception as e:
                        logger.critical(f"Error executing SynAction {sync_action.sync_event.id}")
                        sync_action.sync_event.status = 'failed'
                        sync_action.sync_event.execution_log = traceback.format_exc()
                        sync_action.sync_event.description = str(e)
                        session.add(sync_action.sync_event)
                        logger.info('Deleting queue element'.format(sync_action.id))
                        session.query(SyncActionsQueue).filter(SyncActionsQueue.id == sync_action.id).delete()
            except Exception as e:
                # Fallback if session is corrupted.
                if sync_action_id is not None:
                    with sessionMaker.session_scope_threaded() as session_error:
                        sync_action = session_error.query(SyncActionsQueue).filter(
                            SyncActionsQueue.id == sync_action_id
                        ).first()
                        sync_action.sync_event.status = 'failed'
                        sync_action.sync_event.execution_log = traceback.format_exc()
                        sync_action.sync_event.description = str(e)
                        session_error.query(SyncActionsQueue).filter(SyncActionsQueue.id == sync_action.id).delete()
                        session_error.add(sync_action.sync_event)
                logger.critical(f"Unhandled Error in except clause Sync Action ID: {sync_action_id}")
