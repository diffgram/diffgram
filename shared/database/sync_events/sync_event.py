# OPENCORE - ADD
from shared.database.common import *


class SyncEvent(Base):
    """
        AKA: Streaming

        SyncEvent tracks all internal events from files and tasks inside Diffgram.
        This table should have all the info related to file moves, copy, deletions
        and metadata
    """
    __tablename__ = 'sync_event'
    id = Column(BIGINT, primary_key=True)

    # Where this sync event came from. Might be blank in case of Drag an drop or connection file addition.
    # In this case you will have an input_id for tracking.
    dataset_source_id = Column(Integer, ForeignKey('working_dir.id'))
    dataset_source = relationship("WorkingDir",
                                  uselist=False,
                                  foreign_keys=[dataset_source_id])

    # Where the sync ended up moving the file (In case we have dir to dir sync events in future)
    dataset_destination_id = Column(Integer, ForeignKey('working_dir.id'))
    dataset_destination = relationship("WorkingDir",
                                       uselist=False,
                                       foreign_keys=[dataset_destination_id])

    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    # General text description.
    description = Column(String())

    # For knowing which file was synced, and even go deeper in relations to know the input for example.
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys=[file_id])

    # The job context on where this sync happened.
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")

    # Input file
    input_id = Column(Integer, ForeignKey('input.id'))
    input = relationship("Input", foreign_keys=[input_id])

    # For knowing in what project did the sync occurred.
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])

    # For knowing which task was created.
    created_task_id = Column(Integer, ForeignKey('task.id'))
    created_task = relationship("Task", foreign_keys=[created_task_id])

    # For knowing which task was completed in case of task completion.
    completed_task_id = Column(Integer, ForeignKey('task.id'))
    completed_task = relationship("Task", foreign_keys=[completed_task_id])

    # Store the new file that was copied from the extisting file in case of a copy sync event, else will be null.
    new_file_copy_id = Column(Integer, ForeignKey('file.id'))
    new_file_copy = relationship("File", foreign_keys=[new_file_copy_id])

    # In case of a file event, will store the specific file action/
    transfer_action = Column(String())  # ["move", "copy",  "mirror"]

    # Any errors, tracebacks or relevant information will be stored here.
    execution_log = Column(String())
    """
    The concept I have for the sync events is this:
        - I specify I desired state in Diffgram, by creating task templates. For example, I want all labeled files 
          from X job to go to Y dir. 
        - Diffgram makes sure to match the desired state by generating a series of sync events.
        - Sync events are triggered by some action
        - Sync events have some sort of effect that helps get closer or match the user desired state of the data.
    """

    # This column specifies what effect will the sync event had i.e transfer actions.
    # Move a file, copy a file, delete it, etc.
    event_effect_type = Column(String())  # ["move_file", "copy_file", "remove_file", "add_file", "create_task].

    # This column specifies what trigger the sync event to be created,Task completion, External provider webhook, etc.
    event_trigger_type = Column(String())  # ["task_completed", "file_added"]

    # For queueing purposes. All objects with this value true will be processed by a deferred worker process/thread.
    processing_deferred = Column(Boolean(), default=False)

    # For future retry mechanisms or querying failed sync events in a date range.
    time_last_attempted = Column(Integer)

    status = Column(String(), default="init")  # ["init", "completed", "failed"]

    # Might be useful in future for some realtime visualizations on progress bars or something similar.
    percent_complete = Column(Float, default=0.0)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    def serialize(self):
        result =  {
            'id': self.id,
            'dataset_source_id': self.dataset_source_id,
            'dataset_destination_id': self.dataset_destination_id,
            'created_date': self.created_date,  # str() is to help with nesting json stuff
            'description': self.description,
            'file_id': self.file_id,
            'input_id': self.input_id,
            'project_id': self.project_id,
            'created_task_id': self.created_task_id,
            'completed_task_id': self.completed_task_id,
            'new_file_copy_id': self.new_file_copy_id,
            'transfer_action': self.transfer_action,
            'event_effect_type': self.event_effect_type,
            'event_trigger_type': self.event_trigger_type,
            'processing_deferred': self.processing_deferred,
            'time_last_attempted': self.time_last_attempted,
            'status': self.status,
            'percent_complete': self.percent_complete,
            'member_created_id': self.member_created_id,
            'member_updated_id': self.member_updated_id,
        }

        if self.dataset_source:
            result['dataset_source'] = {'nickname': self.dataset_source.nickname, 'id': self.dataset_source_id}
        if self.dataset_destination:
            result['dataset_destination'] = {'nickname': self.dataset_destination.nickname, 'id': self.dataset_destination_id}
        if self.file:
            result['file'] = {'original_filename': self.file.original_filename, 'id': self.file.id}
        if self.job:
            result['job'] = {'id': self.job.id, 'name': self.job.name}
        return result

