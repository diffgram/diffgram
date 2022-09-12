# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.job.job import Job


@routes.route('/api/v1/job/<int:task_template_id>/add-files', methods = ['POST'])
@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor"],
    apis_project_list = [],
    apis_user_list = ["api_enabled_builder"])
def task_template_add_files_api(task_template_id):
    """
        Creates tasks for the given file id list or diffgram query value.
    :param task_template_id:
    :return:
    """
    spec_list = [
        {"file_id_list": {
            'required': False,
            'kind': list
        }
        },
        {"query": {
            'required': False,
            'kind': str
        }
        },
    ]

    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        members_serialized, log = task_template_add_files_core(session = session,
                                                               task_template_id = task_template_id,
                                                               file_id_list = task_template_id,
                                                               query = None,
                                                               log = log)
        return jsonify(members_serialized), 200


def task_template_add_files_core(session, task_template_id, file_id_list = None, query = None, log = regular_log.default()):
    task_template = Job.get_by_id(session, task_template_id)
    if task_template is None:
        log['error']['task_template'] = "Task Template does not exists."
        return False, log

    reviewers = task_template.get_reviewers(session)

    assignees = task_template.get_assignees(session)
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
