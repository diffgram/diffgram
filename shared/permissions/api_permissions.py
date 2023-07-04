# OPENCORE - ADD
from shared.database.auth.api import Auth_api
from shared.shared_logger import get_shared_logger
from flask import request

logger = get_shared_logger()

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

    @staticmethod
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
        logger.debug(f'Checking Permissions: {auth}')
        if auth is None:
            logger.warning(f'Auth API was not found for client ID: {client_id}')
            return False
        logger.debug(f'Checking Permissions: {auth.project_string_id} - {auth.is_valid} - {auth.permission_level} ')
        if auth.is_valid != True:
            logger.warning(f'Auth API is invalid ')
            return False

        if auth.client_secret != client_secret:
            logger.warning(f'Auth API client secret does not match ')
            return False

        if auth.project_string_id != project_string_id:
            logger.warning(f'Auth Project string ID does not match ')
            return False

        if auth.permission_level in Roles:
            return True
        logger.warning(f'Invalid Roles. Auth role is {auth.permission_level} but allowed roles are {Roles}')
        return False
