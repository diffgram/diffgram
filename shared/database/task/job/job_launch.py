# OPENCORE - ADD
from shared.database.common import *
from shared.database.task.task import Task
from shared.database.task.job.user_to_job import User_To_Job
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.connection.connection import Connection
from shared.database.external.external import ExternalMap


class JobLaunch(Base):
    """
    A job has many tasks.

    ***

    add stuff to copy_job_for_exam() if adding things

    ***

    """

    __tablename__ = 'job_launch'
    id = Column(Integer, primary_key=True)

    # The job/task_template that will be launched.
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job")

    status = Column(String(), default="started")

    job_launch_info = Column(String(), default="started")
    # started, in_progress, retrying failed.

    percent_complete = Column(Float, default=0.0)  # caching a value here for easy front end consumption

    log = Column(MutableDict.as_mutable(
        JSONEncodedDict))  # eg may store regular log here, maybe better here then current job.launch_attempt_log
    retry_count = Column(Integer, default=0)

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys=[member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys=[member_updated_id])

    time_created = Column(DateTime, default=datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    time_intial_setup_completed = Column(
        DateTime)  # eg for debugging external setups, seperating general object creation from tasks
    time_completed = Column(DateTime)

    def serialize_for_list_view(self, session):

        return {
            'id': self.id,
            'status': self.status,
            'job_launch_info': self.job_launch_info,
            'percent_complete': self.percent_complete,
            'time_created': self.time_created,
            'time_completed': self.time_completed,
            'log': self.log,
            'job_name': self.job.name,
            'job_id': self.job.id
        }

    @staticmethod
    def new(session=None, add_to_session=False, flush_session=False, job=None, job_id=None, status=None,
            member_created=None, member_updated=None):
        job_launch = JobLaunch(
            job=job,
            job_id=job_id,
            status=status,
            member_created=member_created,
            member_updated=member_updated,
            time_created=datetime.datetime.now(),
            time_updated=datetime.datetime.now(),
        )
        if add_to_session:
            session.add(job_launch)
        if flush_session:
            session.flush()
        return job_launch

    @staticmethod
    def get_by_id(session, job_launch_id=None):
        return session.query(JobLaunch).filter(
            JobLaunch.id == job_launch_id
        ).first()


class JobLaunchQueue(Base):
    __tablename__ = 'job_launch_queue'
    id = Column(Integer, primary_key=True)

    # The job/task_template that will be launched.
    job_launch_id = Column(Integer, ForeignKey('job_launch.id'))
    job_launch = relationship("JobLaunch")

    # The higher the number the higher the priority.
    priority = Column(Integer(), default=1)

    @staticmethod
    def add_to_queue(session=None, add_to_session=False, flush_session=False, job_launch=None, priority=1):
        job_launch_queue = JobLaunchQueue(
            job_launch=job_launch,
            priority=priority,
        )
        if add_to_session:
            session.add(job_launch_queue)
        if flush_session:
            session.flush()
        return job_launch_queue
