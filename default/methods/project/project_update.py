# OPENCORE - ADD
# Import necessary modules and functions
from methods.regular.regular_api import *
from shared.database.deletion import Deletion

# Define the route for updating a project with appropriate HTTP method and permissions
@routes.route('/api/v1/project/<string:project_string_id>' +              '/update',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
# Define the api_project_update function to handle the route
def api_project_update(project_string_id):
    """
    This function handles the API route for updating a project.
    It performs necessary validations, security checks, and recovery steps.

    Considerations:
    1) Security: Ensure that only authorized users with appropriate roles can update a project.
    2) Recovery: Provide logging and error handling to ensure data integrity and ease of troubleshooting.

    * removing a user from a projects permissions effectively hides it...
    """
    # Define the list of expected input specifications
    spec_list = [{'mode': str}]

    # Call the master function from regular_input to process the request and get log, input, and untrusted_input
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)

    # If there are any errors in the input, return a bad request response with the log
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    # Begin a session with the database
    with sessionMaker.session_scope() as session:

        # Fetch the user and project based on the provided user and project string ID
        user = User.get(session = session)
        project = Project.get(session, project_string_id)

        # Call the project_update_core function to process the project update
        log = project_update_core(
            session = session,
            project = project,
            mode = input['mode'],
            log = log,
            member = user.member)

        # If there are any errors in the log, return a bad request response with the log
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        # Update the log with a success message and serialize the project object
        log['success'] = True
        return jsonify(
            log = log,
            project = project.serialize()), 200

# Define the project_update_core function to process the project update
def project_update_core(session,
                        project,
                        mode,
                        log,
                        member):
    """
    This function processes the core steps required to update a project,
    including sending emails, creating deletion objects, removing permissions,
    and updating the project's status.

    Considerations:
    1) Security: Ensure that only authorized users can perform specific update actions.
    2) Recovery: Provide logging and error handling to ensure data integrity and ease of troubleshooting.

    * Send email
    * Create deletion thing to track it
    * Remove permissions for all users (including Admin?)
    * Remove from project
    * Set project flag to deleted
    """
    # Check if the mode is DELETE
    if mode == "DELETE":

        # Create a new Deletion object and add it to the session
        deletion = Deletion(project = project,
                            member_created = member)
        session.add(deletion)
        session.add(project)

        # Set the project's deletion_pending flag to True
        project.deletion_pending = True

        # Initialize the deletion.cache dictionary
        deletion.cache = {}

        # Iterate through all users in the project and remove their permissions
        for user in project.users:
            deletion.cache['permissions'] = {}

            # user_id : user permissions for project
            deletion.cache['permissions'][user.id] = user.permissions_projects[project.project_string_id]

            # Call the Project_permissions.clear_all function to remove the user's permissions
            Project_permissions.clear_all(
                session = session,
                user = user,
                sub_type = project.project_string_id)

        # Remove the database link to the project by setting the users list to an empty list
        project.users = []

        # Add a log message for removing the project
        log['info']['remove'] = "Project scheduled for deletion."

        # Prepare email details
        email = member.user.email
        subject = f"{project.project_string_id} scheduled for deletion."
        message = project.project_string_id + \
                  " may be deleted in approximately 30 days." + \
                  " Please contact us immediately if you did not authorize this change."

        # Call the communicate_via_email.send function to send the email
        communicate_via_email.send(email, subject, message)

        # Create a new Event object and add it to the session
        Event.new(
            kind = "project_delete",
            session = session,
            member = member,
            success = True
        )

    # Check if the mode is MAKE_PUBLIC
    if mode == "MAKE_PUBLIC":

        # If the project is already public, add an error message to the log
        if project.is_public is True:
            log['error']['public'] = "Project already public"
            return log

        # Add the project to the session and set its is_public flag to True
        session.add(project)
        project.is_public = True

        # Add a log message for making the project public
        log['info']['public'] = "Project now public."

        # Prepare email details
        email = member.user.email
        subject = f"{project.project_string_id} now public."
        message = project.project_string_id + \
                  " is now publicly accessible." + \
                  " Please contact us immediately if you did not authorize this change."

        # Call the communicate_via_email.send function to send the email
        communicate_via_email.send(email, subject, message)

        # Create a new Event object and add it to the session
        Event.new(
            kind = "project_make_public",
            session = session,
            member = member,
            success = True
        )

    # Check if the mode is MAKE_PRIVATE
    if mode == "MAKE_PRIVATE":

        # If the project is already private, add an error message to the log
        if project.is_public is False:
            log['error']['public'] = "Project already private"
            return log

        # Add the project to the session and set its is_public flag to False
        session.add(project)
        project.is_public = False

        # Add a log message for making the project private
        log['info']['public'] = "Project now private."

        # Create a new Event object and add it to the session
        Event.new(
            kind = "project_make_private",
            session = session,
            member = member,
            success = True
        )

    # Return the updated log
    return log
