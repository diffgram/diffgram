# OPENCORE - ADD
from shared.database.auth.api import Auth_api

from flask import request


class API_Permissions():

    # Probably a bettter name...
    def by_project(session,
                   project_string_id,
                   Roles):

        client_id = request.authorization.get('username', None)
        client_secret = request.authorization.get('password', None)

        if not client_id:
            return False

        if not client_secret:
            return False

        auth_result = API_Permissions.auth_api_permissions(
            session = session,
            client_id = client_id,
            client_secret = client_secret,
            project_string_id = project_string_id,
            Roles = Roles)

        return auth_result

    def auth_api_permissions(session,
                             client_id,
                             client_secret,
                             project_string_id,
                             Roles):
        """
        Returns True if:
            Auth exists and is valid
            Client secret, project string, and role level matches
        """

        # Gets actual auth object

        auth = Auth_api.get(session, client_id)

        if auth is None:
            return False

        if auth.is_valid != True:
            return False

        if auth.client_secret != client_secret:
            return False

        if auth.project_string_id != project_string_id:
            return False

        if auth.permission_level in Roles:
            return True

        return False
