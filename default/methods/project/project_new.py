# Import necessary modules and functions
from methods.regular.regular_api import *
import re
from shared.database.labels.label_schema import LabelSchema

# Regular expression patterns for valid project name and ID
project_name_regular_expression = re.compile(r"^[a-zA-Z0-9_ ]{4,30}$")
project_id_regular_expression = re.compile(r"^[a-zA-Z0-9_-]{4,30}$")

# Function to validate project name
def valid_project_name(name):
    """Check if the given project name matches the regular expression pattern"""
    return project_name_regular_expression.match(name)

# Function to validate project ID
def valid_project_id(id):
    """Check if the given project ID matches the regular expression pattern"""
    return project_id_regular_expression.match(id)

# API route for creating a new project
@routes.route('/api/project/new', methods=['POST'])
@General_permissions.grant_permission_for(Roles='normal_user', apis_user_list=['api_enabled_builder'])  # Permission check
@limiter.limit("25 per day")
def project_new_api():
    """
    Create a new project with the given input and user information.
    Check for input validity, user permissions, and project uniqueness.
    Return a JSON response with success or error messages.
    """
    spec_list = [{'project_name': str},
                 {'goal': None},
                 {'project_string_id': str}]

    # Validate and parse the input
    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)

    # Return an error if there are any issues with the input
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # Begin a new session and get the current user and member
    with sessionMaker.session_scope() as session:
        user = User.get(session=session)
        member = get_member(session)

        # Check if only super admins can create projects and if the user is not a super admin
        if settings.ONLY_SUPER_ADMINS_CREATE_PROJECTS and not user.is_super_admin:
            log['error']['unauthorized'] = "Only super admins can create project."
            return jsonify(log=log), 403

        # Check if the user's email is verified
        if user.security_email_verified is not True:
            log['error']['security_email_verified'] = "Please verify your email first"
            return jsonify(log=log), 400

        # Check if a project with the same project_string_id already exists
        existing_project = session.query(Project).filter(
            Project.project_string_id == input['project_string_id']).first()

        if existing_project is not None:
            log['error']['project_string_id'] = "Project name already exists. Projects must be globally unique."
            return jsonify(log=log), 400

        # Set the default project limit for non-super admins
        default_project_limit = 10

        # If the user is not a super admin, check if they have reached the project limit
        if user.is_super_admin != True:
            if len(user.projects) >= default_project_limit:
                log['error']['limit'] = "oops looks like you have a few projects already! Please contact us to increase this limit."
                return jsonify(log=log), 400

        # Validate the project name and ID
        if not valid_project_name(input['project_name']):
            log['error']['project_name'] = "Invalid name."
            return jsonify(log=log), 400

        if not valid_project_id(input['project_string_id']):
            log['error']['project_id'] = "Invalid project id"
            return jsonify(log=log), 400

        # Create a new project with the validated input and user information
        project = Project.new(
            session=session,
            name=input['project_name'],
            project_string_id=input['project_string_id'],
            goal=input['goal'],
            user=user,
            member_created=user.member
        )

        # Return a JSON response with success and project information
        log['success'] = True
        return jsonify(log=log,
                       schema=project.get_default_schema(session).serialize(),
                       project=project.serialize()), 200
