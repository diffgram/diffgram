# OPENCORE - ADD
from methods.regular.regular_api import *
import re

project_name_regular_expression = re.compile(r"^[a-zA-Z0-9_ ]{4,30}$")
project_id_regular_expression = re.compile(r"^[a-zA-Z0-9_-]{4,30}$")


def valid_project_name(name):
    return project_name_regular_expression.match(name)


def valid_project_id(id):
    return project_id_regular_expression.match(id)


@routes.route('/api/project/new', methods=['POST'])
@General_permissions.grant_permission_for(
    Roles='normal_user',
    apis_user_list=[
        'api_enabled_builder'])  # Checking email is verified within function to return nice error message here
@limiter.limit("25 per day")
def project_new_api():
    spec_list = [{'project_name': str},
                 {'goal': None},
                 {'project_string_id': str}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)

        if user.security_email_verified is not True:
            log['error']['security_email_verified'] = "Please verify your email first"
            return jsonify(log=log), 400

        existing_project = session.query(Project).filter(
            Project.project_string_id == input['project_string_id']).first()

        if existing_project is not None:
            log['error']['project_string_id'] = "Project name already exists. Projects must be globally unique."
            return jsonify(log=log), 400

        default_project_limit = 10

        if user.is_super_admin != True:

            """
            When we create a new project we don't have a great way 
            to get the user's "plan" to check if on free plan etc. 
            As a temporary work around, if the user is part of an org we increase limit
            """

            if len(user.projects) >= default_project_limit:
                log['error'][
                    'limit'] = "oops looks like you have a few projects already! Please contact us to increase this limit."
                return jsonify(log=log), 400

        if not valid_project_name(input['project_name']):
            log['error']['project_name'] = "Invalid name."
            return jsonify(log=log), 400

        if not valid_project_id(input['project_string_id']):
            log['error']['project_id'] = "Invalid project id"
            return jsonify(log=log), 400


        project = Project.new(
            session=session,
            name=input['project_name'],
            project_string_id=input['project_string_id'],
            goal=input['goal'],
            user=user,
            member_created=user.member
        )

        log['success'] = True
        return jsonify(log=log,
                       project=project.serialize()), 200
