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
    job = relationship("Job")

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
        return self.to_dict()

    @staticmethod
    def generate_task_creation_event(task) -> 'TaskEvent':
        return TaskEvent.new(
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_created',
        )

    @staticmethod
    def generate_task_completion_event(task) -> 'TaskEvent':
        return TaskEvent.new(
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_completed',
        )

    @staticmethod
    def generate_task_review_start_event(task) -> 'TaskEvent':
        return TaskEvent.new(
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_review_start',
        )

    @staticmethod
    def generate_task_request_change_event(task) -> 'TaskEvent':
        return TaskEvent.new(
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_request_changes',
        )

    @staticmethod
    def new(project_id: int,
            job_id: int,
            task_id: int,
            event_type: str,
            ) -> 'TaskEvent':
        return TaskEvent(

        )
