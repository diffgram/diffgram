# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion


@routes.route('/api/v1/project/<string:project_string_id>/discussions/list', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "allow_if_project_is_public"], apis_user_list = ["api_enabled_builder"])
def discussion_list_web(project_string_id):
    """
        List all the discussion based on the given filters.
        We can filter by job_id, task_id, file_id, status and project.
    :param project_string_id:
    :return:
    """
    issue_list_spec_list = [
        {"task_id": {
            'kind': int,
            "required": False
        }},
        {"file_id": {
            'kind': int,
            "required": False
        }},
        {"starts": {
            'kind': str,
            "required": False
        }},
        {"type": {
            'kind': str,
            "required": False
        }},
        {"ends": {
            'kind': str,
            "required": False
        }},
        {"job_id": {
            'kind': int,
            "required": False
        }},
        {"status": {
            'kind': str,
            "required": False
        }},
        {"members_list": {
            'kind': list,
            "required": False
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_list_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)
        if user:
            member = user.member
        else:
            if request.authorization:
                client_id = request.authorization.get('username', None)
                auth = Auth_api.get(session, client_id)
                member = auth.member

        issues_data, log = issue_list_core(
            session = session,
            log = log,
            project_id = project.id,
            task_id = input['task_id'],
            file_id = input['file_id'],
            job_id = input['job_id'],
            status = input['status'],
            starts = input['starts'],
            type = input['type'],
            ends = input['ends'],
            members_list = input['members_list'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(issues = issues_data), 200


def issue_list_core(session: object,
                    log: dict = regular_log.default(),
                    project_id: int = None,
                    task_id: int = None,
                    file_id: int = None,
                    job_id: int = None,
                    status: str = 'open',
                    starts: str = None,
                    type: str = None,
                    ends: str = None,
                    members_list: list = []):
    """
        Returns serialized dictionary of the list of issues that match the given filters.
        This method assumes data has been validated previously, so no extra validations are done in the function.

    :param session:
    :param log:
    :param project_id:
    :param task_id:
    :param file_id:
    :param job_id:
    :param status:
    :param members_list:
    :return:
    """
    if project_id is None:
        log['error']['project_id'] = 'Provide project_id'
        return None, log

    issues = Discussion.list(
        session = session,
        project_id = project_id,
        task_id = task_id,
        file_id = file_id,
        job_id = job_id,
        status = status,
        starts = starts,
        ends = ends,
        type = type,
        members_list = members_list
    )

    issue_data = [issue.serialize_for_list() for issue in issues]
    return issue_data, log
