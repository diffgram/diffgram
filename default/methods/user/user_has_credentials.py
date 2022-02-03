# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from flask import Response
from shared.database.task.credential.credential import Credential
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job
from methods.task.credential.credential_list import credential_view_core
from flask import jsonify


@routes.route('/api/v1/project/<string:project_string_id>/user/<int:user_to_check_id>/has-credentials',
              methods = ['GET'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "allow_if_project_is_public"],
                                      apis_user_list = ["api_enabled_builder"])
def api_user_has_credentials(project_string_id, user_to_check_id) -> [Response, int]:
    """
        List all the discussion based on the given filters.
        We can filter by job_id, task_id, file_id, status and project.
    :param project_string_id:
    :return:
    """
    spec_list = [
        {"task_template_id": {
            'kind': str,
            "required": True
        }},
    ]
    data = request.args

    log = regular_log.default()
    log, input = regular_input.input_check_many(
        log = log,
        untrusted_input = data,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        print('user_to_check_id', user_to_check_id)
        user = User.get_by_id(session, user_to_check_id)
        print('user', user)
        credentials_data, log = user_has_credentials_core(
            session = session,
            log = log,
            user = user,
            project = project,
            task_template_id = input['task_template_id']
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(credentials_data), 200


def user_has_credentials_core(session: object,
                              log: dict,
                              user: User,
                              project: Project,
                              task_template_id: int) -> [dict, dict]:
    if project is None:
        log['error']['project_id'] = 'Provide project_id'
        return None, log

    if user is None:
        log['error']['user_id'] = 'User does not exist'
        return None, log

    if task_template_id is None:
        log['error']['task_template_id'] = 'Provide task_template_id'
        return None, log

    user_credentials = Credential.get_by_user_id(
        session = session,
        user_id = user.id
    )
    user_credential_type_id_list = [x.credential_type_id for x in user_credentials]

    task_template = Job.get_by_id(session, task_template_id)

    if task_template is None:
        log['error']['task_template'] = 'Task Template does not exist'
        return None, log

    required_credentials_rels = Credential_Type_To_Job.get_by_job_id(
        session = session,
        job_id = task_template_id,
        requires_only = True
    )

    print('REQURIEDD', required_credentials_rels)
    required_credentials = [x.credential_type for x in required_credentials_rels]

    missing_credentials = []
    for cred in required_credentials:
        if cred.id not in user_credential_type_id_list:
            missing_credentials.append(cred)

    result = {
        'missing_credentials': [x.serialize_for_list_view() for x in missing_credentials],
        'has_credentials': len(missing_credentials) == 0
    }
    return result, log
