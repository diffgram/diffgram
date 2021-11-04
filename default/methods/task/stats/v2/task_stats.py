from methods.regular.regular_api import *
from shared.database.task.job.job import Job

@routes.route('/api/v2/job/<job_id>/stat', methods=["GET"])
def job_stat(job_id):
    with sessionMaker.session_scope() as session:
        job = Job.get_by_id(session, job_id)
        print(job)
        return f'Works {job_id}'