from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin


class TaskEvent(Base, SerializerMixin):
    """
        AKA: Streaming

        TaskEvents track all the actions or occurences related with a task. For example a change of status,
        archiving a task, creating a task or any other action related with a task object.
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

    event_type = Column(String())  # ["completed", "archived",  "in_review", "created"]

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    def serialize(self):
        return self.to_dict(rules = (
            '-member_created',
            '-member_updated',
            '-job',
            '-task',
            '-project'))

    @staticmethod
    def generate_task_creation_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_created',
        )

    @staticmethod
    def generate_task_completion_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_completed',
        )

    @staticmethod
    def generate_task_review_start_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_review_start',
        )

    @staticmethod
    def generate_task_request_change_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_request_changes',
        )

    @staticmethod
    def generate_task_review_complete_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_review_complete',
        )

    @staticmethod
    def generate_task_in_progress_event(session, task) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_in_progress',
        )

    @staticmethod
    def new(session: 'Session',
            project_id: int,
            job_id: int,
            task_id: int,
            event_type: str,
            add_to_session: bool = True,
            flush_session: bool = True
            ) -> 'TaskEvent':

        task_event = TaskEvent(
            project_id = project_id,
            job_id = job_id,
            task_id = task_id,
            event_type = event_type,
        )

        if add_to_session:
            session.add(task_event)
        if flush_session:
            session.flush()
        return task_event
