from functools import wraps

from shared.database.user import User
from shared.database.project import Project
from shared.database.auth.api import Auth_api

from werkzeug.exceptions import Forbidden
from shared.helpers.permissions import getUserID
from shared.helpers.permissions import LoggedIn
from shared.helpers.permissions import defaultRedirect
from shared.helpers import sessionMaker

from flask import request
from shared.permissions.api_permissions import API_Permissions
from shared.permissions.user_permissions import User_Permissions

default_denied_message = "(Project Scope) No access."


class Project_permissions():

    def user_has_project(Roles,
                         apis_project_list = [],
                         apis_user_list = ["security_email_verified"]):
        """
        Defaults to forbidden if no match found

        Arguments:
            Roles, list of strings, ie ['allow_anonymous', 'editor']
        Matching:
        1. Attempts to find match for project string
        2. If found, attempts to find match for permissions for that project
        3. If found, returns function.

        Exceptions:

        'allow_anonymous'
        user.is_super_admin

        NOTE this is "just" the wrapper
        use check_permissions() for inside a function.

       """
        if not isinstance(Roles, list): Roles = [Roles]

        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwds):
                project_string_id = kwds.get('project_string_id', None)

                # We expect this to raise
                Project_permissions.by_project_core(
                    project_string_id = project_string_id,
                    Roles = Roles,
                    apis_project_list = apis_project_list,
                    apis_user_list = apis_user_list
                )

                # If we get here in execution it's allowed
                return func(*args, **kwds)

            return inner

        return wrapper

    @staticmethod
    def check_basic_auth_exists():
        if request.headers:
            user_agent = request.headers.get('User-Agent')
            if user_agent and len(user_agent) >= 6:
                if user_agent[:6] == "python":
                    if request.authorization is None:
                        raise Forbidden(
                            "Check client_id client_secret - Missing sending basic auth while using python SDK.")

    @staticmethod
    def by_project_core(
        project_string_id: str,
        Roles: list,
        apis_project_list: list = [],
        apis_user_list: list = []
    ):

        with sessionMaker.session_scope() as session:
            if not project_string_id or project_string_id == "null" or project_string_id == "undefined":
                raise Forbidden(default_denied_message + " [ First Sanity Checks ] project_string_id None, null, etc.")

            project = Project.get(session, project_string_id)
            if project is None:
                raise Forbidden("Can't find project")

            if Project_permissions.check_if_project_is_public(project, Roles):
                return True

            if request.authorization is not None:

                basic_auth_denied_message = default_denied_message + " [Basic Auth Based] "

                client_id = request.authorization.get('username', None)
                if not client_id:
                    raise Forbidden(basic_auth_denied_message + " No username. (client_id)")
                client_secret = request.authorization.get('password', None)
                if not client_secret:
                    raise Forbidden(basic_auth_denied_message + " No password. (client_secret)")

                result = API_Permissions.by_project(session = session,
                                                    project_string_id = project_string_id,
                                                    Roles = Roles)
                if result is not True:
                    raise Forbidden(basic_auth_denied_message + "Failed API Permissions")

                # Project APIs, maybe should role this into API_Permissions
                check_all_apis(
                    project = project,
                    apis_required_list = apis_project_list)

                return True

            user_denied_message = default_denied_message + " [Human User Based] "

            result = Project_permissions.check_permissions(
                session = session,
                apis_project_list = apis_project_list,
                apis_user_list = apis_user_list,
                project_string_id = project_string_id,
                Roles = Roles,
                user_denied_message = user_denied_message,
                project = project)

            if result is True:
                return True
            else:
                raise Forbidden(user_denied_message)

    @staticmethod
    def check_if_project_is_public(project, Roles):
        # Just becuase a project is public
        # Doesn't mean public is allowed acccess to all
        # routes. ie only admins can delete project

        if 'allow_if_project_is_public' in Roles:
            if project:
                if project.is_public is True:
                    return True

        return False

    # Assumes in the context of a user - not basic auth
    @staticmethod
    def check_permissions(Roles,
                          project_string_id,
                          session,
                          apis_project_list = None,
                          apis_user_list = None,
                          user_denied_message = None,
                          project = None):
        """

        """
        if user_denied_message is None:
            user_denied_message = default_denied_message

        if project_string_id is None:
            # TODO merge None checks from other thing up top here.
            raise Forbidden(user_denied_message + "project_string_id is None")

		if Project_permissions.check_if_project_is_public(project, Roles):
			return True
        if 'allow_anonymous' in Roles:
            return True

        if project is None:
            project = Project.get(session, project_string_id)
            if project is None:
                raise Forbidden(user_denied_message + " Failed to Get Project ")

            if Project_permissions.check_if_project_is_public(project, Roles):
                return True

        # Must come after public project check, otherwise blocks public projects since auth is None
        # Must come before a human user based check like LoggedIn()
        Project_permissions.check_basic_auth_exists()

        # TODO merge LoggedIn() with getUserID() similar internal logic
        if LoggedIn() != True:
            raise Forbidden(user_denied_message + " Failed LoggedIn ")

        if 'allow_any_logged_in_user' in Roles:  # TODO not happy with this name, want more clarity on how this effects other permissions like apis / project etc.
            return True

        user = session.query(User).filter(User.id == getUserID()).one()

        if user.is_super_admin == True:
            return True

        if apis_project_list:
            check_all_apis(project = project,
                           apis_required_list = apis_project_list)

        if apis_user_list:
            User_Permissions.general(user = user,
                                     apis_user_list = apis_user_list)

        # This could be slow if a user has a lot of projects?
        for project, Permissions in user.permissions_projects.items():

            if Permissions is None:
                continue

            if project_string_id == project:
                check_role_result = check_roles(Roles, Permissions)
                if check_role_result is True:
                    return True

        # Default
        # Good to have this here so we can call
        # this function as one line and don't ahve to worry
        # About returning False (must have returned True eariler)
        raise Forbidden(user_denied_message)

    def remove(permission, user, sub_type):
        current_permissions = user.permissions_projects[sub_type]
        current_permissions.remove(permission)
        user.permissions_projects[sub_type] = current_permissions

    def add(permission, user, sub_type):
        """
        permission, string
        user, user object
        sub_type, ie project_string_id

        if permission in current_permissions we return to avoid adding it twice
        returns True, None on success
        returns False, "error message" on error
        """
        current_permissions = user.permissions_projects.get(sub_type, None)
        if current_permissions is None:
            current_permissions = []
        if permission in current_permissions:
            return False, "Already has permission"
        current_permissions.append(permission)
        user.permissions_projects[sub_type] = current_permissions
        return True, None

    def clear_all(user, sub_type):
        user.permissions_projects[sub_type] = {}


def check_roles(Roles, Permissions):
    for role in Roles:
        if role in Permissions:
            return True


# TODO combine this with user method
# TODO rename this, "apis" is confusing in context
# of APU Auth, this is an API flag check? think on name
def check_all_apis(project,
                   apis_required_list):
    if not apis_required_list:
        return True

    for api in apis_required_list:
        check_api(apis_required_list = apis_required_list,
                  api_to_check = api,
                  project = project)


def check_api(apis_required_list,
              api_to_check,
              project):
    """
    apis_required, a list of names of apis that
    are required

    If an API is in the list, it must be enabled
    """
    if getattr(project, api_to_check) is not True:
        raise Forbidden(api_to_check + " not enabled.")
