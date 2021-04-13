# OPENCORE - ADD
from dataclasses import dataclass
from functools import wraps
import datetime
from shared.database.sync_events.sync_event import SyncEvent


@dataclass
class SyncEventManager:
    sync_event: any
    session: any

    def _with_sync_event(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            if not inst.sync_event:
                return
            return f(inst, *args, **kwargs)

        return wrapped

    @_with_sync_event
    def set_status(self, new_status):
        self.sync_event.status = new_status

    @_with_sync_event
    def add_create_task(self, task):
        self.sync_event.created_task = task
        self.session.add(self.sync_event)

    @_with_sync_event
    def set_dataset_destination(self, dataset):
        self.sync_event.dataset_destination = dataset
        self.session.add(self.sync_event)

    @_with_sync_event
    def set_description(self, description):
        self.sync_event.description = description
        self.session.add(self.sync_event)

    @_with_sync_event
    def set_transfer_action(self, transfer_action):
        self.sync_event.transfer_action = transfer_action
        self.session.add(self.sync_event)

    @_with_sync_event
    def set_event_effect_type(self, effect_type):
        self.sync_event.event_effect_type = effect_type
        self.session.add(self.sync_event)

    @staticmethod
    def create_sync_event_and_manager(
            session=None,
            dataset_source=None,
            dataset_source_id=None,
            dataset_destination=None,
            dataset_destination_id=None,
            description=None,
            file=None,
            job=None,
            input=None,
            input_id=None,
            project=None,
            status=None,
            created_task=None,
            completed_task=None,
            new_file_copy=None,
            transfer_action=None,
            event_effect_type=None,
            event_trigger_type=None,
            processing_deferred=None,
            member_created=None,
            member_updated=None
    ):
        """
        Creates a sync event an returns the sync_event_manager.
        :param session:
        :param dataset_source:
        :param dataset_source_id:
        :param dataset_destination:
        :param dataset_destination_id:
        :param description:
        :param file:
        :param job:
        :param input:
        :param project:
        :param status:
        :param created_task:
        :param completed_task:
        :param new_file_copy:
        :param transfer_action:
        :param event_effect_type:
        :param event_trigger_type:
        :param processing_deferred:
        :param member_created:
        :param member_updated:
        :return:
        """
        sync_event = SyncEvent(
            dataset_source=dataset_source,
            dataset_source_id=dataset_source_id,
            dataset_destination=dataset_destination,
            dataset_destination_id=dataset_destination_id,
            description=description,
            file=file,
            job=job,
            input=input,
            input_id=input_id,
            project=project,
            created_task=created_task,
            completed_task=completed_task,
            new_file_copy=new_file_copy,
            transfer_action=transfer_action,
            event_effect_type=event_effect_type,
            event_trigger_type=event_trigger_type,
            processing_deferred=processing_deferred,
            member_created=member_created,
            member_updated=member_updated,
            status=status
        )
        session.add(sync_event)
        session.flush()
        manager = SyncEventManager(session=session, sync_event=sync_event)
        return manager
