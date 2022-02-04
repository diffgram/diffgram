from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import desc
from sqlalchemy.orm.session import Session
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class TaskTimeTracking(Base, SerializerMixin):
    """
        Aggregate table to track time spend per user across
        tasks.
    """
    __tablename__ = 'task_time_tracking'
    id = Column(BIGINT, primary_key = True)

    # The job context on where this sync happened.
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys = [job_id])

    # For knowing in what project did the sync occurred.
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys = [project_id])

    # For knowing which task was created.
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys = [file_id])

    parent_file_id = Column(Integer, ForeignKey('file.id'), nullable = True)
    parent_file = relationship("File", foreign_keys = [parent_file_id])

    # This includes all the task statuses + "before_complete", "after_complete", "
    status = Column(String, nullable = True, default = None)

    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys = [user_id])

    time_spent = Column(Float, default = 0.0)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    @staticmethod
    def get_global_record_from_status_record(session: Session, status_record: 'TaskTimeTracking') -> 'TaskTimeTracking':

        global_record = session.query(TaskTimeTracking).filter(
            TaskTimeTracking.job_id == status_record.job_id,
            TaskTimeTracking.job_id == status_record.job_id,
            TaskTimeTracking.task_id == status_record.task_id,
            TaskTimeTracking.project_id == status_record.project_id,
            TaskTimeTracking.user_id == status_record.user_id,
            TaskTimeTracking.file_id == status_record.file_id,
            TaskTimeTracking.parent_file_id == status_record.parent_file_id,
            TaskTimeTracking.status == None,
        ).first()
        return global_record

    @staticmethod
    def new_or_update(session,
                      job_id: int,
                      task_id: int,
                      project_id: int,
                      status: str,
                      user_id: int,
                      time_spent: float,
                      file_id: int,
                      parent_file_id: int = None,
                      add_to_session: bool = True,
                      flush_session: bool = True) -> 'TaskTimeTracking':
        """
            Create a new time record or updates the existing one.

            We always have a global (status=null) timer
            and a timer per status on the task (status record).

            Each time we update the time, we replace the global record
            with the new global time spent, and calculate the delta from last
            record to get the new time spent on the specific status record.
        :param session:
        :param job_id:
        :param task_id:
        :param project_id:
        :param status:
        :param user_id:
        :param time_spent:
        :param file_id:
        :param parent_file_id:
        :param add_to_session:
        :param flush_session:
        :return:
        """

        time_track_record = session.query(TaskTimeTracking).filter(
            TaskTimeTracking.job_id == job_id,
            TaskTimeTracking.task_id == task_id,
            TaskTimeTracking.project_id == project_id,
            TaskTimeTracking.user_id == user_id,
            TaskTimeTracking.file_id == file_id,
            TaskTimeTracking.parent_file_id == parent_file_id,
            TaskTimeTracking.status == status,
        ).first()

        time_track_record_global = session.query(TaskTimeTracking).filter(
            TaskTimeTracking.job_id == job_id,
            TaskTimeTracking.task_id == task_id,
            TaskTimeTracking.project_id == project_id,
            TaskTimeTracking.user_id == user_id,
            TaskTimeTracking.file_id == file_id,
            TaskTimeTracking.parent_file_id == parent_file_id,
            TaskTimeTracking.status.is_(None)
        ).first()

        existing_global_record = True
        if time_track_record_global is None:
            # Create new Record
            logger.info('New Global Track Time Record task_id:{} status:{} user_id:{}'.format(task_id, status, user_id))
            time_track_record_global = TaskTimeTracking(
                job_id = job_id,
                task_id = task_id,
                user_id = user_id,
                project_id = project_id,
                time_spent = time_spent,
                parent_file_id = parent_file_id,
                file_id = file_id,
            )
            existing_global_record = False
            if add_to_session:
                session.add(time_track_record_global)


        existing_status_record = True
        if time_track_record is None:
            logger.info('New Status Track Time Record task_id:{} status:{} user_id:{}'.format(task_id, status, user_id))
            # Create a status specific record
            time_track_record = TaskTimeTracking(
                job_id = job_id,
                task_id = task_id,
                user_id = user_id,
                project_id = project_id,
                time_spent = time_spent,
                parent_file_id = parent_file_id,
                file_id = file_id,
                status = status
            )
            existing_status_record = False
            if add_to_session:
                session.add(time_track_record)

        if existing_global_record or existing_status_record:
            # Update Record
            logger.info('Update Track Time Record task_id:{} status:{} user_id:{}'.format(task_id, status, user_id))
            old_global_time = time_track_record_global.time_spent
            if old_global_time < time_spent:
                new_time_spent_delta = time_spent - old_global_time
                # We replace the global time with the new time
                time_track_record_global.time_spent = time_spent
                if existing_status_record:
                    # We add the delta time to the give status record.
                    time_track_record.time_spent += new_time_spent_delta
                else:
                    time_track_record.time_spent = new_time_spent_delta
        if add_to_session:
            session.add(time_track_record_global)
            session.add(time_track_record)
        if flush_session:
            session.flush()

        return time_track_record
