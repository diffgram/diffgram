try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import Role
from shared.database.project import PROJECT_DEFAULT_ROLES


@routes.route('/api/v1/project/<string:project_string_id>/roles/new', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin"], apis_user_list = ["api_enabled_builder"])
def new_role_web(project_string_id):
    """
        Creates a new role in the project for permissions management.
    :param project_string_id:
    :return:
    """
    issue_new_spec_list = [
        {"name": {
            'kind': str
        }},
        {"permissions_list": {
            'kind': list,
            "required": False
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
        role_data, log = new_role_core(
            session = session,
            log = log,
            member = member,
            project = project,
            name = input['name'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(role_data), 200


def new_role_core(session,
                  log = regular_log.default(),
                  member = None,
                  project = None,
                  name = None,
                  ):
    if project is None:
        log['error']['project'] = 'Provide project for role creation.'
        return None, log

    if name is None:
        log['error']['name'] = 'Provide name for role creation.'
        return None, log

    if name.lower() in PROJECT_DEFAULT_ROLES:
        log['error']['name'] = f'Invalid role name. This role name is part of default roles {RESERVED_ROLES}'
        return None, log

    existing_role = Role.get_by_name_and_project(
        session = session,
        project_id = project.id,
        name = name
    )
    if existing_role is not None:
        role_data = existing_role.serialize()
        return role_data, log

    role = Role.new(
        session = session,
        project_id = project.id,
        name = name,
    )

    role_data = role.serialize()
    return role_data, log
