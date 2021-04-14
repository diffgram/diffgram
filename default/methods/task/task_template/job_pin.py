# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.job.job import Job

@routes.route('/api/v1/job/<int:job_id>/pin', methods = ['POST'])
@Job_permissions.by_job_id(
	project_role_list = ["admin", "Editor"],
	apis_project_list = [],
	apis_user_list=["api_enabled_builder"])
def job_pin_api(job_id):

    # PIN is at the "project level" eg for all users the job is pinned.
    # this is different from other "star" concepts which may be used specific
    
    spec_list = []
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        job_serialized = job_pin_core(session = session, job_id = job_id)
        return jsonify(job = job_serialized, log = log), 200


def job_pin_core(session, job_id):
    job = Job.get_by_id(session, job_id)

    job.is_pinned = not job.is_pinned

    return job.serialize_minimal_info()
