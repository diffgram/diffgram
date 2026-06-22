# OPENCORE - ADD
import random
import string

from methods.regular.regular_api import *  # Import regular_api methods

from shared.database import hashing_functions  # Import hashing functions

from shared.database.auth.api import Auth_api  # Import Auth_api class
from shared.database.auth.member import Member  # Import Member class

# Define the route for creating a new API key for a project
@routes.route('/api/v1/project/<string:project_string_id>/auth/api/new',
              methods=['POST'])
@Project_permissions.user_has_project(["admin"])
def auth_api_credential_new_from_api(project_string_id):
    """
    Endpoint to provision a new API key.

    Arguments:
        project_string_id (String): The string ID of the project.

    Returns:
        jsonify() response: A JSON response containing the log and, if successful,
                            the auth credentials.
    """
    spec_list = [{'permission_level': str},
                 {'is_live': bool}]

    # Validate and sanitize the input.
    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # Check if the permission level is valid.
    if input['permission_level'] not in ["Editor", "Viewer", "admin"]:
        log["errors"]["permission_level"] = "permission_level invalid"
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        # Main function to create a new Auth_api object.
        auth = create(session,
                      project_string_id,
                      input['permission_level'],
                      input['is_live'])

        # Prepare the response.
        log["success"] = True
        return jsonify(log=log,
                       auth=auth.serialize_with_secret()), 200

# Function to create a new Auth_api object.
def create(session,
           project_string_id,
           permission_level,
           is_live):
    """
    Creates new Auth_api object.

    Arguments:
        session (db object): The database session object.
        project_string_id (string): The string ID of the project.
        permission_level (string): The permission level of the API key.
        is_live (bool): A flag indicating if the API key is for live or test.

    Returns:
        Auth object: The created Auth_api object.
    """

    auth = Auth_api()  # Create a new Auth_api object.
    session.add(auth)  # Add the object to the session.

    member = Member()  # Create a new Member object.
    session.add(member)  # Add the object to the session.
    member.kind = "api"  # Set the member type to 'api'.

    session.flush()  # Flush the session to get the IDs of the created objects.

    member.auth_api = auth  # Associate the Auth_api object with the Member object.
    auth.member_id = member.id  # Set the member ID in the Auth_api object.

    auth.permission_level = permission_level  # Set the permission level.
    auth.project_string_id = project_string_id  # Set the project string ID.
    auth.is_live = is_live  # Set the live/test flag.

    auth = create_client_auth_pair(auth)  # Generate client ID and secret.

    project = Project.get(session, project_string_id)  # Get the project object.
    auth.project_id = project.id  # Set the project ID in the Auth_api object.

    # Assign the project roles.
    Project_permissions.assign_project_roles(session=session,
                                             role_name=permission_level.lower(),
                                             project=project,
                                             log=regular_log.default(),
                                             member_id=member.id)

    logger.info(f'Assigned role {permission_level} to project {project.project_string_id} and member {member.id}')

    # Create the event for the new API auth.
    user = User.get(session=session)
    Event.new(session=session,
              kind="new_api_auth",
              member_id=user.member_id,
              success=True,
              project_id=project.id,
              email=user.email)

    return auth

# Function to generate client ID and secret.
def create_client_auth_pair(auth):
    """
    Random id / secret creation and adding to Auth object.

    Caution:
        Assumes auth.is_live is set

    Arguments
        Auth (Auth_api object): The Auth_api object.

    Returns
        Auth (Auth_api object): The Auth_api object with client ID and secret.
    """

    # Generate the client ID based on the is_live flag.
    if auth.is_live == True:
        auth.client_id = "LIVE__"
    else:
        auth.client_id = "TEST__"

    auth.client_id += create_random_string(length=20)
    auth.client_secret = create_random_string(length=60)

    return auth

# Function to create a random string.
def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase +
                                 string.digits) for x in range(length))
