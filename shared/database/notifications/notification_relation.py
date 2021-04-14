# OPENCORE - ADD
from shared.database.common import *


class NotificationRelation(Base):
    """
    One Notification to Many NotificationRelations

    But for now we just assume it's 1:1 and store it on  Notification?
    """

    __tablename__ = 'notification_relation'
    id = Column(Integer, primary_key=True)

    # Not used yet because we default to 1:1
    notification_id = Column(Integer, ForeignKey('notification.id'))
    notification = relationship("Notification", foreign_keys=[notification_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", foreign_keys=[project_id])

    input_id = Column(Integer, ForeignKey('input.id'))
    input = relationship("Input", foreign_keys=[input_id])

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys=[task_id])

    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys=[job_id])

    member_id = Column(Integer, ForeignKey('member.id'))
    member = relationship('Member', foreign_keys=[member_id])

    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", foreign_keys=[file_id])

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'))
    working_dir = relationship("WorkingDir", foreign_keys=[working_dir_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    @staticmethod
    def new(session=None,
            add_to_session=False,
            flush_session=False,
            project_id=None,
            input_id=None,
            task_id=None,
            member_id=None,
            job_id=None,
            working_dir_id=None,
            file_id=None):

        notification_relation = NotificationRelation(
            project_id=project_id,
            input_id=input_id,
            task_id=task_id,
            job_id=job_id,
            member_id=member_id,
            working_dir_id=working_dir_id,
            file_id=file_id,
        )
        if add_to_session:
            session.add(notification_relation)
        if flush_session:
            session.flush()
        return notification_relation

    @staticmethod
    def get_by_id(session, job_launch_id=None):
        return session.query(NotificationRelation).filter(
            NotificationRelation.id == job_launch_id
        ).first()

