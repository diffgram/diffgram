# OPENCORE - ADD
try:
    from default.methods.regular.regular_api import *
except:
    from methods.regular.regular_api import *

from abc import ABC, abstractmethod
from shared.utils.source_control.file.file_transfer_core import file_transfer_core
from shared.database.sync_events.sync_action_queue import SyncActionsQueue
from shared.helpers.sessionMaker import AfterCommitAction

class Observable(ABC):
    """
        This abstract class is for defining an observable object in diffgram.
        The idea is that is observable object will force any other class that uses it
        to implement the behaviour of adding observers and removing them.
    """

    @abstractmethod
    def _add_observer(self, observer):
        raise NotImplementedError

    @abstractmethod
    def _remove_observer(self, observer):
        raise NotImplementedError

    @abstractmethod
    def notify_all_observers(self, type, defer):
        raise NotImplementedError


class Observer(ABC):
    """
        This abstract class is for defining an observer object in diffgram.
        The idea is that is observer object will force any other class that uses it
        to implement the behaviour of updating their state based on changes sent by an
        Observable object.
    """

    @abstractmethod
    def _update_observer(self, action_type=None):
        raise NotImplementedError


class JobObservable(Observable):
    """
        This class will take care of all the operation related to notifying users about a change
        in the state of the job.
        Currently we are only interested on any of the job's task being completed, but this can expand
        to any change on the job state and notify any observers of this job about the state update.
    """

    def __init__(self, session, log, job, task=None, sync_events_manager=None):
        """

        :param dir_observer_list: The directories that are observing the job for new updates.
        """
        if job is None:
            raise ValueError('Provide a job object to create a job observable')
        self.job = job
        # The specific task to observe from this job.
        self.task = task
        self.session = session
        self.log = log
        # Dirs observers is a list of DirectoryJobObserver objects. We need to build it based on the DB data
        self.dir_observer_list = []
        self.sync_events_manager = sync_events_manager
        # For now we only have 1 possible observer so array will only have the job.completion_directory observer.
        dir_job_observer = DirectoryJobObserver(
            session,
            log,
            directory=job.completion_directory,
            job_observable=self)

        self.dir_observer_list.append(dir_job_observer)

    def _add_observer(self,
                      observer):
        # TODO: for now we currently support just 1 observer (ie output directory). Might support multiple in future.
        self.job.completion_directory = observer

    def add_new_directory_observer(self,
                                   directory_observer):
        self._add_observer(directory_observer.directory)

    def _remove_observer(self,
                         observer):
        # TODO: for now we currently support just 1 observer so remove will just set the completion_dir to None.
        self.job.completion_directory = None

    def remove_directory_observer(self,
                                  directory_observer):
        if self.job.completion_directory != directory_observer.directory:
            return
        self._remove_observer(directory_observer.directory)


    # Could also call this notify_all() and then notify_single() or something...
    def notify_all_observers(self,
                             type: str = 'task_complete',      # Default to task_complete
                             defer=True):

        if self.task.job_id != self.job.id:
            logger.error("self.task.job_id != self.job.id")
            return

        for observer in self.dir_observer_list:
            self._execute_single_observer(
                observer=observer,
                type=type,
                defer=defer
            )

    # WIP WIP WIP
    def _execute_single_observer(
            self,
            observer,
            type: str,
            defer: bool):

        # For now we only notify task completions. We can add more types in the future for other actions.
        if type == 'task_complete':
            # Default action upon task complete is to move/push files
            # Maybe a more specific name to moving/updating files rather then update? not sure.
            observer.copy_or_move_to_dir(
                defer=defer,
                trigger_type=type)

    def get_task(self):
        return self.task


class DirectoryJobObserver(Observer):
    """
        This class is for implementing a directory job observer. It encapsulates the concept
        of a WorkingDirectory object watching for changes on a Job. For now it is only concerned
        about new completed tasks, but new logic can be added to support other types of updates/changes.

    """

    def __init__(self,
                 session,
                 log,
                 directory,
                 job_observable):
        self.session = session
        self.log = log
        self.directory = directory
        self.job_observable = job_observable

    def _perform_file_copy(self):
        file_transfer_core(
            session=self.session,
            source_directory=self.job_observable.task.incoming_directory,
            destination_directory=self.job_observable.task.job.completion_directory,
            transfer_action='copy',
            copy_instances=True,
            file=self.job_observable.task.file,
            log=self.log,
            sync_event_manager=self.job_observable.sync_events_manager,
            defer_sync=False
        )

    def _perform_file_move(self):
        file_transfer_core(
            session=self.session,
            source_directory=self.job_observable.task.incoming_directory,
            destination_directory=self.job_observable.task.job.completion_directory,
            transfer_action='move',
            file=self.job_observable.task.file,
            log=self.log,
            sync_event_manager=self.job_observable.sync_events_manager,
            defer_sync=False
        )

    def update_sync_event_data(self, action_type, trigger_type=None):
        if self.job_observable.sync_events_manager and self.job_observable.job.completion_directory:
            if trigger_type == 'task_complete':
                self.job_observable.sync_events_manager.set_status('completed')
                self.job_observable.sync_events_manager.set_dataset_destination(
                    dataset=self.job_observable.task.job.completion_directory
                )
                desc = 'Completed task ID: {} and perform operation "{}" to dataset {}'.format(
                    self.job_observable.task.id,
                    action_type,
                    self.job_observable.task.job.completion_directory.nickname
                    )
                self.job_observable.sync_events_manager.set_description(desc)
                self.job_observable.sync_events_manager.set_transfer_action(action_type)
                self.job_observable.sync_events_manager.set_event_effect_type(f"{action_type}_file")
                logger.debug(desc)

    def _update_observer(self, action_type=None, trigger_type=None):
        # Copy or move the file depending on the job action specifications.

        if action_type == 'copy':
            self._perform_file_copy()
        elif action_type == 'move':
            self._perform_file_move()

        # Add relevant data to sync event object.
        self.update_sync_event_data(action_type=action_type, trigger_type=trigger_type)

    def enqueue_dir_update(self):
        if self.job_observable.sync_events_manager:
            logger.debug('Deferring sync action for update_directory in file_observers.')
            SyncActionsQueue.enqueue(self.session, self.job_observable.sync_events_manager.sync_event)
            AfterCommitAction(
                session = self.session,
                callback = regular_methods.transmit_interservice_request,
                callback_args = {
                    'message': 'new_sync_action_item',
                    'logger': logger,
                    'service_target': 'walrus'
                }
            )

    def copy_or_move_to_dir(self, defer=True, trigger_type=None):
        if not defer:
            action_type = self.job_observable.job.output_dir_action
            self._update_observer(action_type=action_type, trigger_type=trigger_type)
        else:
            self.enqueue_dir_update()
