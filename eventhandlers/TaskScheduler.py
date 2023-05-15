from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from shared.settings import settings
from shared.shared_logger import get_shared_logger
from shared.helpers import sessionMaker

logger = get_shared_logger()
# TODO: move this module to its own independent service to allow eventhandlers to scale horizontally.
class SchedulerService:
    scheduler: BackgroundScheduler
    def __init__(self, scheduler: BackgroundScheduler):
        self.scheduler = scheduler
    def exposed_add_job(self, func, *args, **kwargs):
        return self.scheduler.add_job(func, *args, **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return self.scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        return self.scheduler.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, jobstore=None):
        return self.scheduler.pause_job(job_id, jobstore)

    def exposed_resume_job(self, job_id, jobstore=None):
        return self.scheduler.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, jobstore=None):
        self.scheduler.remove_job(job_id, jobstore)

    def exposed_get_job(self, job_id):
        return self.scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return self.scheduler.get_jobs(jobstore)

class DiffgramTaskScheduler:
    scheduler: BackgroundScheduler
    manager: SchedulerService
    def __init__(self, db_engine):
        self.scheduler = BackgroundScheduler(
            jobstores = {'default': SQLAlchemyJobStore(engine = db_engine, url = settings.DATABASE_URL)}
        )
        self.manager = SchedulerService(scheduler = self.scheduler)

    def check_locks_and_start(self):
        self.manager.scheduler.start()

        logger.info('Task Scheduler Started')

diffgram_scheduler = DiffgramTaskScheduler(db_engine = sessionMaker.engine)