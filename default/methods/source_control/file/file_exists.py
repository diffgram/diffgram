# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment


@routes.route('/api/v1/project/<string:project_string_id>/file/exists',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def file_list_exists_api(project_string_id):
    """
        Given a file list, checks if the file list exists.
    :param project_string_id:
    :return:
    """
    file_list_exists_spec = [
        {"file_id_list": {
            'kind': list
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = file_list_exists_spec)

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

        result, log = file_list_exists_core(
            session = session,
            log = log,
            project = project,
            file_id_list = input['file_id_list'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(exists = result), 200


def file_list_exists_core(session,
                          project,
                          file_id_list,
                          log = regular_log.default()):
    """
        Give the file id list, check that all files exists on the project,
    :param session:
    :param file_id_list:
    :param log:
    :return:
    """
    try:
        file_list_db = File.get_files_in_project_id_list(session, project.id, file_id_list)
        db_id_dict = {}
        for f in file_list_db:
            db_id_dict[f.id] = True
        result = True
    except Exception as e:
        log['error']['file_list'] = str(e)
        return False, log
    
    for id in file_id_list:
        if not db_id_dict.get(id):
            result = False
            break
    return result, log
