# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.query_engine.query_creator import QueryCreator


@routes.route('/api/v1/project/<string:project_string_id>/query-suggest', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def query_suggest_web(project_string_id):
    """
        List all the discussion based on the given filters.
        We can filter by job_id, task_id, file_id, status and project.
    :param project_string_id:
    :return:
    """
    issue_list_spec_list = [
        {"query": {
            'kind': str,
            "required": True,
            "string_len_not_zero": False
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_list_spec_list,
        string_len_not_zero = False)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        query_data, log = query_suggest_core(
            session = session,
            log = log,
            project = project,
            query = input['query'],
            member = member,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(query_data), 200


def query_suggest_core(session: object,
                       log: dict = regular_log.default(),
                       project: Project = None,
                       query: str = None,
                       member: object = None):
    """
        Returns suggestions based on query provided.

    :param session:
    :param log:
    :param project_id:
    :param query:
    :return:
    """
    if project is None:
        log['error']['project'] = 'Provide project'
        return None, log

    query_creator = QueryCreator(session, project, member)
    suggestions, type = query_creator.get_suggestions(query)
    return {'suggestions': suggestions, 'type': type}, log
