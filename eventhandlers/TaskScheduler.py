from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from shared.settings import settings
from shared.shared_logger import get_shared_logger
from shared.helpers import sessionMaker

logger = get_shared_logger()


# TODO: move this module to its own independent service to allow eventhandlers to scale horizontally.
class DiffgramTaskScheduler:
    scheduler: BackgroundScheduler
    store: SQLAlchemyJobStore

    def __init__(self, scheduler: BackgroundScheduler):
        self.scheduler = scheduler

    def add_job(self, job_id: str, cron_expr: str, func, *args, **kwargs):

        return self.scheduler.add_job(func = func,
                                      trigger =  CronTrigger.from_crontab(cron_expr),
                                      id = job_id,
                                      *args,
                                      **kwargs)

    def modify_job(self, job_id, **changes):
        return self.scheduler.modify_job(job_id, **changes)

    def reschedule_job(self, job_id, trigger: str = 'cron', **trigger_args):
        return self.scheduler.reschedule_job(job_id,
                                             trigger = trigger,
                                             **trigger_args)

    def pause_job(self, job_id):
        return self.scheduler.pause_job(job_id)

    def resume_job(self, job_id):
        return self.scheduler.resume_job(job_id)

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

    def get_job(self, job_id):
        return self.scheduler.get_job(job_id)

    def get_jobs(self, jobstore = None):
        return self.scheduler.get_jobs(jobstore)

    def __init__(self, db_engine):
        self.store = SQLAlchemyJobStore(engine = db_engine, url = settings.DATABASE_URL)
        self.scheduler = BackgroundScheduler(
            jobstores = {'default': self.store}
        )

    def start(self):
        self.scheduler.start()
        logger.info('Task Scheduler Started')


diffgram_scheduler = DiffgramTaskScheduler(db_engine = sessionMaker.engine)
