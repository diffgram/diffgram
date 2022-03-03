# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.job.job import Job


@routes.route('/api/v1/job/<int:task_template_id>/members-list', methods = ['GET'])
@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor"],
    apis_project_list = [],
    apis_user_list = ["api_enabled_builder"])
def task_template_members_list_api(task_template_id):
    # PIN is at the "project level" eg for all users the job is pinned.
    # this is different from other "star" concepts which may be used specific
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        members_serialized, log = task_template_members_list_core(session = session, job_id = task_template_id, log=log)
        return jsonify(members_serialized), 200


def task_template_members_list_core(session, job_id, log):
    task_template = Job.get_by_id(session, job_id)
    if task_template is None:
        log['error']['task_template'] = "Task Template does not exists."
        return False, log

    reviewers = task_template.get_reviewers(session)

    assignees = task_template.get_assignees(session)
    print('assignees', assignees)
    print('reviewers', assignees)
    reviewers_serialized = []
    for user in reviewers:
        reviewers_serialized.append(user.serialize())

    assignees_serialized = []
    for user in assignees:
        assignees_serialized.append(user.serialize())

    return {
        "reviewers": reviewers_serialized,
        "assignees": assignees_serialized
    }, log
