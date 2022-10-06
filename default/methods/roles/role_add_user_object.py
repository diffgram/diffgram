try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import RoleMemberObject, Role
from shared.database.auth.member import Member


@routes.route('/api/v1/project/<string:project_string_id>/role-member-object', methods = ['PATCH'])
@Project_permissions.user_has_project(Roles = ["admin"], apis_user_list = ["api_enabled_builder"])
def new_role_member_object_web(project_string_id):
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
        {"object_id": {
            'kind': int
        }},
        {"role_id": {
            'kind': int
        }},
        {"member_id": {
            'kind': int
        }},
        {"default_role_name": {
            'kind': str
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session = session)
        assignment_data, log = new_role_member_object_core(
            session = session,
            log = log,
            project = project,
            member_id = input['member_id'],
            role_id = input['role_id'],
            object_type = input['object_type'],
            object_id = input['object_id'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(assignment_data), 200


def new_role_member_object_core(session,
                                member_id: int,
                                project: Project,
                                role_id: int,
                                object_id: int,
                                object_type: str,
                                log = regular_log.default(),
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

    member = Member.get_by_id(session, member_id = member_id)
    has_member = project.has_member(member_id = member.id)
    if not has_member:
        log['error']['member_id'] = 'member_id does not belong to project.'
        return None, log

    valid, log = RoleMemberObject.check_object_type(obj_type = object_type, log = log)
    if regular_log.log_has_error(log):
        return None, log
    from shared.database.permissions.roles import ValidObjectTypes
    role_member_object = RoleMemberObject.new(
        session = session,
        object_id = object_id,
        object_type = ValidObjectTypes[object_type],
        role_id = role_id,
        member_id = member_id
    )

    data = role_member_object.serialize()
    return data, log
