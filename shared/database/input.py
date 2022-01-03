# OPENCORE - ADD
from shared.database.common import *
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.regular import regular_log
from sqlalchemy import event as sqlalchemy_event


from sqlalchemy.schema import Index
from sqlalchemy.dialects.postgresql import JSONB

class Input(Base):
    __tablename__ = 'input'

    id = Column(Integer, primary_key=True)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    time_completed = Column(DateTime)
    time_loaded_video = Column(DateTime)

    # We assume this includes upload
    time_video_write_finished = Column(DateTime)

    # Frames can start processing as this happens
    # But it's still an "end point" to measure
    # ie we could look at other options to speed that up.
    time_pushed_all_frames_to_queue = Column(DateTime)

    # Yes some work to update this
    # BUT this is probably a better measure for more closely tracking
    # if the process crashes so worth it.
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    time_last_attempted = Column(Integer)

    # TODO list available modes here...
    mode = Column(String) 

    url = Column(String())
    media_type = Column(String())  # image, frame, video, csv

    #  Why not name this "source"
    # TODO naming of this attribute could probably be improved.
    type = Column(String())  # ["from_url", "from_video_split"]

    allow_csv = Column(Boolean())

    allow_duplicates = Column(Boolean(), default=False)

    # By default we don't defer processing, but can if needed
    # At the moment this flag is only used "in flight"
    # So eventually, in theory, all the flags will be False.
    # Not sure if that's ok or bad?
    processing_deferred = Column(Boolean(), default=False)

    status = Column(String(), default="init")
    status_text = Column(String())

    offset_in_seconds = Column(Integer)
    percent_complete = Column(Float, default=0.0)

    description = Column(String())
    size = Column(Integer)

    archived = Column(Boolean, default=False)


    raw_data_blob_path = Column(String())
    # video_processed_blob_path = Column(String())


    resumable_url = Column(String())

    # For AWS S3 Uploads
    upload_aws_id = Column(String())
    upload_aws_parts_list = Column(MutableDict.as_mutable(JSONEncodedDict))

    # For Azure Uploads
    upload_azure_block_list = Column(MutableDict.as_mutable(JSONEncodedDict))

    video_split_duration = Column(Integer())
    # For now inferring from video_split_duration
    # if it exists then we assume we want to split it
    video_was_split = Column(Boolean)

    retry_log = Column(MutableDict.as_mutable(JSONEncodedDict))

    # I think it would be good for this to be seperate
    # For easy searching
    # Default to 0 so we can do < a value instead of None checks
    retry_count = Column(Integer, default=0)

    # Use get_by_id().
    # See parent_input =  in process_media.py
    parent_input_id = Column(Integer, ForeignKey('input.id'))
    # parent_input = relationship("Input", foreign_keys=[parent_input_id])

    # context of say a video file
    parent_file_id = deferred(Column(Integer, ForeignKey('file.id')))
    parent_file = relationship("File", foreign_keys=[parent_file_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys=[file_id])

    newly_copied_file_id = Column(Integer, ForeignKey('file.id'))
    newly_copied_file = relationship("File", foreign_keys=[newly_copied_file_id]) #TODO: ADD TO PRODUCTION

    add_link = Column(Boolean)
    remove_link = Column(Boolean)
    copy_instance_list = Column(Boolean, default = False)

    sequence_map = Column(MutableDict.as_mutable(JSONEncodedDict))

    file_metadata = Column(MutableDict.as_mutable(JSONB))

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys=[task_id])
    task_action = Column(String())

    external_map_id = Column(Integer, ForeignKey('external_map.id'))
    external_map = relationship("ExternalMap", foreign_keys=[external_map_id])
    external_map_action = Column(String())

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")

    # Also include image or video?

    directory_id = Column(Integer, ForeignKey('working_dir.id'))    # target directory
    directory = relationship("WorkingDir", foreign_keys=[directory_id])

    source_directory_id = Column(Integer, ForeignKey('working_dir.id'))     # For internal only
    source_directory = relationship("WorkingDir", foreign_keys=[source_directory_id])

    invalid_directory_permission = Column(Boolean)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User")

    batch_id = Column(Integer, ForeignKey('input_batch.id'))
    batch = relationship("InputBatch", foreign_keys=[batch_id])

    temp_dir = Column(String())

    temp_dir_path_and_filename = Column(String())
    dzuuid = Column(String())
    original_filename = Column(String())
    extension = Column(String())

    instance_list = Column(MutableDict.as_mutable(JSONEncodedDict))
    frame_packet_map = Column(MutableDict.as_mutable(JSONEncodedDict))

    update_log = Column(MutableDict.as_mutable(JSONEncodedDict),
                        default=regular_log.default())  # New Sept 3, 2020

    # Context of video
    video_parent_length = Column(Integer)  # This way don't have to check video each time. To see where it ends

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    __table_args__ = (
        Index('index__processing_deferred__archived',
              "processing_deferred", "archived",
              postgresql_where = (archived.is_(True))),
    )

    def parent_input(self, session):
        if not self.parent_input_id: return None

        return session.query(Input).filter(Input.id == self.parent_input_id).first()

    def child_list(self, session):
        return session.query(Input).filter(Input.parent_input_id == self.id).all()

    @staticmethod
    def new(
            project = None,
            project_id = None,
            media_type: str = None,
            type: str = None,
            mode: str = None,
            url: str = None,
            job_id: int = None,
            video_parent_length: int = None,
            source_directory_id: int = None,
            remove_link: bool = None,
            add_link: bool = None,
            copy_instance_list: bool = None,
            directory_id: int = None,
            file_id: int = None,
            parent_file_id: int = None,
            newly_copied_file_id: int = None,
            sequence_map: dict = None,
            processing_deferred: bool = False,
            parent_input_id: int = None,
            batch_id: int = None,
            video_split_duration: int = None,
            file_metadata: dict = None,
            member_created_id: int = None
    ):
        """
        Helps insure not forgetting stuff...

        does not add to session or flush because we may not
        always want to do that.

        Different ways files can come in here...
        """

        # Careful to check parent otherwise tries to recusrively split.
        # if there is no parent then it's assumed to be the "original"
        # if a video_split is provided then we use it.
        if parent_input_id is None and video_split_duration is None:
            video_split_duration = 30

        input = Input(
            project=project,
            project_id = project_id,
            file_id=file_id,
            mode=mode,
            newly_copied_file_id=newly_copied_file_id,
            media_type=media_type,
            type=type,
            url=url,
            job_id=job_id,
            directory_id=directory_id,
            sequence_map=sequence_map,
            processing_deferred=processing_deferred,
            parent_input_id=parent_input_id,
            video_parent_length = video_parent_length,
            video_split_duration=video_split_duration,
            batch_id=batch_id,
            copy_instance_list=copy_instance_list,
            file_metadata=file_metadata,
            member_created_id=member_created_id
        )
        input.parent_file_id = parent_file_id

        return input

    def get_by_id(
            session,
            id: int,
            skip_locked: bool = False):

        query = session.query(Input).filter(Input.id == id)

        if skip_locked == True:
            query = query.with_for_update(skip_locked=True)

        return query.first()

    def serialize(self):

        directory = None

        if self.directory and not self.invalid_directory_permission:
            directory = self.directory.serialize_simple()

        # Total time
        # TODO maybe look at time last attempted too..
        # ALSO we may want to actually declare a "completion"
        # time, this just assumes it doesn't get updated after
        # completion

        total_time = None
        if self.created_time and self.time_updated:
            total_time = self.time_updated - self.created_time

        return {
            'id': self.id,
            'created_time': self.created_time,
            'time_updated': self.time_updated,
            'total_time': str(total_time),
            'media_type': self.media_type,
            'original_filename': self.original_filename,
            'description': self.description,
            'status': self.status,
            'status_text': self.status_text,
            'directory': directory,
            'percent_complete': self.percent_complete,
            'processing_deferred': self.processing_deferred,
            'time_last_attempted': self.time_last_attempted,
            'retry_log': self.retry_log,
            'retry_count': self.retry_count,
            'video_split_duration': self.video_split_duration,
            'video_was_split': self.video_was_split,
            # For debugging
            'raw_data_blob_path': self.raw_data_blob_path,
            'source': self.type,
            'mode': self.mode,
            'file_id': self.file_id,
            'batch_id': self.batch_id,
            'task_id': self.task_id,  # Include task_id
            'update_log': self.update_log,
            'instance_list': self.instance_list,
            # 'frame_packet_map': self.frame_packet_map,
            'newly_copied_file_id': self.newly_copied_file_id
        }

    def serialize_with_frame_packet(self):
        result = self.serialize()
        result['frame_packet_map'] = self.frame_packet_map
        result['instance_list'] = self.instance_list
        return result

    @staticmethod
    def directory_not_equal_to_status(
            session,
            directory_id,
            status="success",
            return_type="count"
    ):
        """
        Returns 0 if there are no files equal to status
        otherwise returns count of files != to status
        """

        file_link_sub_query = WorkingDirFileLink.get_sub_query(
            session, directory_id)

        assert file_link_sub_query is not None

        # TODO should we exclude
        # failed ones optionally?...
        # We could do status not in list [failed_flag, success] etc..

        query = session.query(Input).filter(
            Input.file_id == file_link_sub_query.c.file_id,
            Input.status != status,
            Input.archived != True)

        if return_type == "count":
            return query.count()

        if return_type == "objects":
            return query.all()
