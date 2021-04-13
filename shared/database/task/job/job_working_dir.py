# OPENCORE - ADD
from shared.database.common import *


class JobWorkingDir(Base):
    """
        This table will keep the relationships between
        Task tempates (Job) and datasets(WorkingDir).
    """
    __tablename__ = 'job_working_dir'
    id = Column(Integer, primary_key=True)

    # The job/task_template that will be launched.
    job_id = Column(Integer, ForeignKey('job.id'))
    job = relationship("Job", foreign_keys=[job_id])

    # Sync, copy_once, inactive.
    sync_type = Column(String, default='sync')

    working_dir_id = Column(Integer, ForeignKey('working_dir.id'))
    working_dir = relationship("WorkingDir", foreign_keys=[working_dir_id])

    @staticmethod
    def new(session=None,
            add_to_session=False,
            flush_session=False,
            job=None,
            sync_type=None,
            working_dir_id=None,
            working_dir=None):
        job_launch_queue = JobWorkingDir(
            job=job,
            working_dir=working_dir,
            working_dir_id=working_dir_id,
            sync_type=sync_type
        )
        if add_to_session:
            session.add(job_launch_queue)
        if flush_session:
            session.flush()
        return job_launch_queue

    
    @staticmethod
    def list(
            session,
            class_to_return,    # Job or WorkingDir
            working_dir_id=None,
            job_id=None,
            sync_type=None):
        
        # I'm not sure if assuming a join here is great.

        query = session.query(class_to_return)

        query = query.join(JobWorkingDir)

        if working_dir_id:
            query = query.filter(JobWorkingDir.working_dir_id == working_dir_id)

        if job_id:
            query = query.filter(JobWorkingDir.job_id == job_id)

        if sync_type:
            query = query.filter(JobWorkingDir.sync_type == sync_type)

        return query.all()

