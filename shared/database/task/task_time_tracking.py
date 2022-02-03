from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import desc
from shared.database.discussion.discussion_comment import DiscussionComment


class TaskTimeTracking(Base, SerializerMixin):
    """
        Aggregate table to track time spend per user across
        tasks.
    """
    __tablename__ = 'task_event'
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

    # This includes all the task statuses + "before_complete", "after_complete", "
    status = Column(String)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", foreign_keys = [task_id])

    time_spent = Column(Float, default = 0.0)

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)
