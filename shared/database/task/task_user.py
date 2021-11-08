from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin


class TaskUser(Base, SerializerMixin):
    """
        For Management of Assignees and Reviewers.
    """
    __tablename__ = 'task_user'
    id = Column(BIGINT, primary_key = True)

    # The job context on where this sync happened.
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", foreign_keys = [task_id])

    # For knowing in what project did the sync occurred.
    user_id = Column(Integer, ForeignKey('userbase.id'))
    user = relationship("User", foreign_keys = [user_id])

    relation = Column(String())  # ["assignee", "reviewer"]

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    def serialize(self):
        return self.to_dict(rules = (
            '-task',
            '-user'))

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

    @staticmethod
    def list(session: 'Session',
             task_id: int = None,
             user_id: int = None,
             job_id: int = None,
             relation: str = None):

        query = session.query(TaskUser)
        if task_id:
            query = query.filter(TaskUser.task_id == task_id)

        if user_id:
            query = query.filter(TaskUser.user_id == user_id)

        if relation:
            query = query.filter(TaskUser.relation == relation)

        if job_id:
            from shared.database.task.task import Task
            query = query.join(Task).filter(
                Task.job_id == job_id
            )

        return query.all()
