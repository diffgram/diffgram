# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.user import Signup_code

from shared.database import hashing_functions
from shared.database.project_perms import ProjectDefaultRoles, ProjectRolesPermissions
from shared.database.permissions.roles import RoleMemberObject, ValidObjectTypes, Role

### NEW NEW NEW ###
## NOT checking code creating NEW one 
# existing is just for magic login that's why it's confusing
def new(session,
        auth_code_type,
        user = None,  # TODO review why using "user" parameter here seems like not needed
        project_string_id = None,
        permission_level = None,
        email_sent_to = None,
        org = None):
    """
    This function creates a new signup code with the given parameters.
    It first checks if an existing code with the same type and email exists.
    If it does, and the code is still valid, it returns False, "Existing code", and the existing code.
    If the existing code is invalid, it invalides the code and continues to create a new one.
    If no existing code is found, it creates a new signup code with the given parameters.

    Returns:
        result (bool): A boolean indicating whether the code was created successfully.
        message (str): A message describing the result of the operation.
        auth (Auth() or None): The created Auth object, or None if an error occurred.
    """
    # Check if existing code
    existing_code = session.query(Signup_code).filter(
        Signup_code.email_sent_to == email_sent_to,
        Signup_code.type == auth_code_type,
        Signup_code.is_available != False,
    ).first()

    if existing_code:
        if existing_code.type == "magic_login":
            if time.time() <= existing_code.created_time_int + 900:
                return False, "Existing code", existing_code
            else:
                session.add(existing_code)
                existing_code.is_available = False

    auth = Signup_code()
    session.add(auth)

    auth.type = auth_code_type
    auth.project_string_id = project_string_id
    auth.permission_level = permission_level
    auth.email_sent_to = email_sent_to
    auth.created_time_int = time.time()

    auth.new_code(session)  # hash generation...

    return True, None, auth


def attempt_redeem_code(session,
                        auth_code,
                        email = None):
    """
    This function attempts to redeem a signup code with the given parameters.
    It first checks if the code exists and if it is still available.
    If the code is not found or is not available, it returns False, "Invalid code", and None.
    If the code is found and is available, it redeems the code and returns True, None, and the signup code object.

    Returns:
        result (bool): A boolean indicating whether the code was redeemed successfully.
        message (str): A message describing the result of the operation.
        signup_code (Auth_code or None): The redeemed Auth_code object, or None if an error occurred.
    """
    auth = session.query(Signup_code).filter(
        Signup_code.code == auth_code).first()

    if auth is None:
        return False, "Invalid code.", None

    if auth.is_available is False:
        return False, "Already redeemed.", None

    if auth.email_sent_to and email:
        if auth.email_sent_to != email:
            return False, f"Code only valid for: {str(auth.email_sent_to)}", None

    if auth.type:

        if auth.type == "magic_login":
            if time.time() >= auth.created_time_int + 900:
                return False, "Expired.", None

        if auth.type == "add_to_project":
            process_project_auth_code(
                session = session,
                new_user = new_user,
              ````
