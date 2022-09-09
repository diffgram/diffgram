try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import Role
from shared.database.auth.member import Member


@routes.route('/api/v1/project/<string:project_string_id>/roles/<int:role_id>/add-perm', methods = ['PATCH'])
@Project_permissions.user_has_project(Roles = ["admin"], apis_user_list = ["api_enabled_builder"])
def role_add_permission_web(project_string_id, role_id):
    """
        Adds a permission to the given role
    :param project_string_id:
    :param role_id:
    :return:
    """
    issue_new_spec_list = [
        {"object_type": {
            'kind': str
        }},
        {"permission": {
            'kind': str
        }}
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session = session)
        role_data, log = role_add_permission_core(
            session = session,
            log = log,
            member = member,
            project = project,
            role_id = role_id,
            object_type = input['object_type'],
            permission = input['permission'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(role_data), 200


def role_add_permission_core(session,
                             log = regular_log.default(),
                             member: Member = None,
                             project: Project = None,
                             role_id: int = None,
                             object_type: str = None,
                             permission: str = None,
                             ):
    if project is None:
        log['error']['project'] = 'Provide project for role creation.'
        return None, log

    if role_id is None:
        log['error']['role_id'] = 'Provide role_id for role creation.'
        return None, log

    role = Role.get_by_id(session, role_id)
    if role is None:
        log['error']['role_id'] = 'Role does not exists.'
        return None, log
    if role.project_id != project.id:
        log['error']['project_id'] = 'Role does not belong to project.'
        return None, log

    role_with_new_perm, log = role.add_permission(
        session = session,
        perm = permission,
        obj_type = object_type,
        log = log
    )
    if regular_log.log_has_error(log):
        return None, log

    role_data = role_with_new_perm.serialize()
    return role_data, log
