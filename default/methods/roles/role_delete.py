try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import Role
from shared.database.auth.member import Member


@routes.route('/api/v1/project/<string:project_string_id>/roles/<int:role_id>/delete', methods = ['DELETE'])
@Project_permissions.user_has_project(Roles = ["admin"], apis_user_list = ["api_enabled_builder"])
def role_delete_web(project_string_id, role_id):
    """
        Deletes the given role
    :param project_string_id:
    :param role_id:
    :return:
    """

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session = session)
        role_data, log = role_delete_core(
            session = session,
            project = project,
            role_id = role_id,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(role_data), 200


def role_delete_core(session,
                                log = regular_log.default(),
                                project: Project = None,
                                role_id: int = None,
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

    session.delete(role)

    role_data = role.serialize()
    return role_data, log
