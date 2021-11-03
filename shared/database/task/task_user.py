from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin


class TaskUser(Base, SerializerMixin):
    """
        For Management of Assignees and Reviewers.
    """
    __tablename__ = 'task_member'
    id = Column(BIGINT, primary_key = True)

    # The job context on where this sync happened.
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    # For knowing in what project did the sync occurred.
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", foreign_keys = [user_id])

    relation = Column(String())  # ["assignee", "reviewer"]

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def serialize(self):
        return self.to_dict(rules = (
            '-task',
            '-member'))

    @staticmethod
    def new(session: 'Session',
            task_id: int,
            user_id: int,
            relation: str,
            add_to_session: bool = True,
            flush_session: bool = True
            ) -> 'TaskUser':

        task_event = TaskUser(
            user_id = user_id,
            task_id = task_id,
            relation = relation,
        )

        if add_to_session:
            session.add(task_event)
        if flush_session:
            session.flush()
        return task_event
