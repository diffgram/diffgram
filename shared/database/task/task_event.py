from shared.database.common import *
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import desc
from shared.database.discussion.discussion_comment import DiscussionComment


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

    event_type = Column(String())  # ["completed", "archived",  "in_review", "created", "comment"]

    comment_id = Column(Integer, ForeignKey('discussion_comment.id'))
    comment = relationship("DiscussionComment", foreign_keys = [comment_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    user_reviewer_id = Column(Integer, ForeignKey('userbase.id'))
    user_reviewer = relationship("User", foreign_keys = [user_reviewer_id])

    user_assignee_id = Column(Integer, ForeignKey('userbase.id'))
    user_assignee = relationship("User", foreign_keys = [user_assignee_id])

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    def serialize(self):
        data = self.to_dict(rules = (
            '-member_created',
            '-member_updated',
            '-job',
            '-user_assignee',
            '-user_reviewer',
            '-task',
            '-comment',
            '-project'))

        if self.comment_id:
            data['comment'] = self.comment.serialize()
        return data

    @staticmethod
    def get_last_task_comment(session, task_id, job_id, project_id):
        latest_comment = session.query(TaskEvent).filter(
            TaskEvent.task_id == task_id,
            TaskEvent.job_id == job_id,
            TaskEvent.project_id == project_id,
            TaskEvent.event_type == 'comment'
        ).order_by(desc(TaskEvent.time_created)).first()

        if (latest_comment == None):
            return ""

        comment_display = session.query(DiscussionComment).filter(DiscussionComment.id == latest_comment.comment_id).first()
        return comment_display.content

    @staticmethod
    def generate_task_creation_event(session, task, member) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_created',
            member_created_id = member.id if member else None
        )

    @staticmethod
    def generate_task_completion_event(session, task, member, task_assignee) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_completed',
            member_created_id = member.id if member else None,
            user_assignee_id = task_assignee.id,
            user_reviewer_id = member.user_id if task.job.allow_reviews else None
        )

    @staticmethod
    def generate_task_review_start_event(session, task, member) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_review_start',
            member_created_id = member.id if member else None,
        )

    @staticmethod
    def generate_task_request_change_event(session, task, member, task_assignee) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_request_changes',
            member_created_id = member.id if member else None,
            user_assignee_id = task_assignee.id,
            user_reviewer_id = member.user_id if task.job.allow_reviews else None
        )

    @staticmethod
    def generate_task_review_complete_event(session, task, member) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_review_complete',
            member_created_id = member.id if member else None
        )

    @staticmethod
    def generate_task_in_progress_event(session, task, member) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'task_in_progress',
            member_created_id = member.id if member else None
        )

    @staticmethod
    def generate_task_comment_event(session, task, member, comment) -> 'TaskEvent':
        return TaskEvent.new(
            session = session,
            project_id = task.project_id,
            job_id = task.job_id,
            task_id = task.id,
            event_type = 'comment',
            member_created_id = member.id if member else None,
            comment_id = comment.id

        )

    @staticmethod
    def new(session: 'Session',
            project_id: int,
            job_id: int,
            task_id: int,
            event_type: str,
            member_created_id: int = None,
            user_reviewer_id: int = None,
            user_assignee_id: int = None,
            comment_id: int = None,
            add_to_session: bool = True,
            flush_session: bool = True
            ) -> 'TaskEvent':

        task_event = TaskEvent(
            project_id = project_id,
            job_id = job_id,
            task_id = task_id,
            event_type = event_type,
            member_created_id = member_created_id,
            user_reviewer_id = user_reviewer_id,
            user_assignee_id = user_assignee_id,
            comment_id = comment_id
        )

        if add_to_session:
            session.add(task_event)
        if flush_session:
            session.flush()
        return task_event
