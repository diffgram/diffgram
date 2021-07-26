from methods.regular.regular_api import *


@routes.route('/api/v1/project/<string:project_string_id>/job/resync',
              methods = ['POST'])
@General_permissions.grant_permission_for(
    Roles = ['normal_user'],
    apis_user_list = ["builder_or_trainer"])
@Project_permissions.user_has_project(["admin", "Editor"])
def job_resync_api(project_string_id):
    """
        Checks for any missing files on the job's datasets
        and sends a resync signal to create task
        in case of missing files.
    :return: http response
    """

    spec_list = [
        {"task_template_id": {
            'required': True,
            'kind': int
        }},
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        resync_result, metadata = job_resync_core(session = session,
                                                  task_template_id = input['task_template_id'],
                                                  log = log)
        return jsonify(resync_result = resync_result,
                       metadata = metadata,
                       log = log), 200


def job_resync_core(session,
                    task_template_id,
                    log):
    """
        Given the JOB id, find all the files with no tasks attached to the job,
        and trigger events to create tasks for them.
    :param session:
    :param job_id:
    :param log:
    :return:
    """
    result = {}
    task_template = Job.get_by_id(session = session, job_id = task_template_id)
    if
    attached_dirs = task_template.get_attached_dirs(sync_types = ['sync'])


    return result, log