# Import necessary modules and functions
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.permissions.roles import Role  # Role class for handling roles
from shared.database.auth.member import Member  # Member class for handling members

# Flask decorator to define the API route and HTTP methods
@routes.route('/api/v1/project/<string:project_string_id>/roles/<int:role_id>/add-perm', methods=['PATCH'])
# Project_permissions decorator to check if the user has the required permissions
@Project_permissions.user_has_project(Roles=["admin"], apis_user_list=["api_enabled_builder"])
def role_add_permission_web(project_string_id, role_id):
    """
        Adds a permission to the given role.
        
        :param project_string_id: The string ID of the project.
        :param role_id: The ID of the role to which the permission will be added.
        :return: A JSON response containing the updated role data or an error message.
    """
    # Define the schema for the request data
    issue_new_spec_list = [
        {"object_type": {
            'kind': str
        }},
        {"permission": {
            'kind': str
        }}
    ]

    # Validate and preprocess the request data
    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=issue_new_spec_list)

    # Return a 400 Bad Request response with an error message if there are any issues with the input
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # Begin a new database session
    with sessionMaker.session_scope() as session:

        # Fetch the project and the authenticated member
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session=session)

        # Add the permission to the role and return the updated role data or an error message
        role_data, log = role_add_permission_core(
            session=session,
            log=log,
            member=member,
            project=project,
            role_id=role_id,
            object_type=input['object_type'],
            permission=input['permission'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Return a 200 OK response with the updated role data
        return jsonify(role_data), 200


def role_add_permission_core(session,
                             log=regular_log.default(),
                             member: Member=None,
                             project: Project=None,
                             role_id: int=None,
                             object_type: str=None,
                             permission: str=None,
                             ):
    """
        Adds a permission to the specified role in the given project.

        :param session: The database session object.
        :param log: The log object for recording errors and messages.
        :param member: The authenticated member making the request.
        :param project: The project to which the role belongs.
        :param role_id: The ID of the role to which the permission will be added.
        :param object_type: The type of the object for which the permission is being added.
        :param permission: The permission to be added.
        :return: A tuple containing the updated role data and the log object.
    """
    # Check if the project is provided and return an error message if it's not
    if project is None:
        log['error']['project'] = 'Provide project for role creation.'
        return None, log

    # Check if the role_id is provided and return an error message if it's not
    if role_id is None:
        log['error']['role_id'] = 'Provide role_id for role creation.'
        return None, log

    # Fetch the role with the given role_id
    role = Role.get_by_id(session, role_id)
    # Return an error message if the role does not exist
    if role is None:
        log['error']['role_id'] = 'Role does not exists.'
        return None, log
    # Return an error message if the role does not belong to the project
    if role.project_id != project.id:
        log['error']['project_id'] = 'Role does not belong to project.'
        return None, log

    # Add the permission to the role and return the updated role data or an error message
    role_with_new_perm, log = role.add_permission(
        session=session,
        perm=permission,
        obj_type=object_type,
        log=log
    )
    if regular_log.log_has_error(log):
        return None, log

    # Serialize the updated role data
    role_data = role_with_new_perm.serialize()
    return role_data, log
