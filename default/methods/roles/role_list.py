try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import Role


@routes.route('/api/v1/project/<string:project_string_id>/roles', methods = ['GET'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "Viewer"], apis_user_list = ["api_enabled_builder"])
def list_roles_web(project_string_id):
    """
        Lists roles on the project
    :param project_string_id:
    :return:
    """
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session = session)
        role_data, log = list_roles_core(
            session = session,
            project = project,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(role_data), 200


def list_roles_core(session: 'Session',
                    project: Project,
                    log: dict = regular_log.default(),

                    ) -> [list, dict]:
    if project is None:
        log['error']['project'] = 'Provide project for role creation.'
        return None, log

    role_list = Role.list(
        session = session,
        project_id = project.id,
    )

    role_data = [role.serialize() for role in role_list]
    return role_data, log
