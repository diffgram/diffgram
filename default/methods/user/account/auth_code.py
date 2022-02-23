# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.database.user import Signup_code

from shared.database import hashing_functions


### NEW NEW NEW ###
## NOT checking code creating NEW one 
# existing is just for magic login that's why it's confusing
def new(session,
        auth_code_type,
        user = None,
        project_string_id = None,
        permission_level = None,
        email_sent_to = None,
        org = None):
    """

    Returns
        result, bool
        message, string
        auth, None or class Auth() object

    """

    # TODO review why using "user" parameter here seems like not needed
    # (ie could just use email_sent_to or email?)

    # Check if existing code
    # Only allow one of each type?

    # THis could get pretty messy with expired codes...

    # TODO not clear on use of this type of filer, ie if using a code to send to multiple
    # orgs...

    existing_code = session.query(Signup_code).filter(
        Signup_code.email_sent_to == email_sent_to,
        Signup_code.type == auth_code_type,
        Signup_code.is_available != False,
    ).first()
    if existing_code:
        if existing_code.type == "magic_login":

            # If code is still valid return code
            # Careful not < > sign flipped vs checking if valid
            # The <= is INVERTED on purpose here since
            # We are retruning if the code IF it's still valid
            # TODO refactor this into a generic check is valid function
            if time.time() <= existing_code.created_time_int + 900:
                return False, "Existing code", existing_code

            # Else invalidate code, and continue to create new one
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

    # if auth_type:
    # if auth_type == "magic_login":
    # Option to expressly declare additional stuff

    # Careful this uses email to generate code
    # So we need to define email first
    auth.new_code(session)  # hash generation...

    return True, None, auth


def attempt_redeem_code(session,
                        auth_code,
                        email = None,
                        new_user = None):
    """
    session, session object
    auth_code, string, unsafe

    #TODO rename auth_code_string?

    checks if code is valid, and if so redeems

    returns True, signup_code object (or None), error_message (or None)

    signup_code has other stuff like project and permissions?

    Returns
        result bool,
        message,
        signup_code, class Auth_code (prior Signup_Code) object



    """
    # Is there a reason we wouldn't just directly filter by the signup code provided?

    # TODO extra handling here if email supplied? ie does signup email match code?

    auth = session.query(Signup_code).filter(
        Signup_code.code == auth_code).first()
    if auth is None:
        return False, "Invalid code.", None

    if auth.is_available is False:
        return False, "Already redeemed.", None

    # Context of verifying
    # a user would create account with same email as we send a signup code to
    if auth.email_sent_to and email:
        if auth.email_sent_to != email:
            return False, "Code only valid for: " + \
                   str(auth.email_sent_to), None

    if auth.type:

        if auth.type == "magic_login":
            # 15 minute (time unit of 1 second * 60 * 15)
            if time.time() >= auth.created_time_int + 900:
                return False, "Expired.", None

        if auth.type == "add_to_project":

            # Careful, now we want auth object
            # TODO clarify this!!!
            process_project_auth_code(
                session = session,
                new_user = new_user,
                auth_code = auth)


        elif auth.type == 'verify_signup':

            user = User.get_by_email(session = session,
                                     email = email)

            # A user may have multiple verify emails
            # We could invalidate all "assoicated" codes,
            # and/or refuse to accept new codes if the user is already verified
            # Context of the user having multiple verify codes,
            # Using the first one, and then still having valid ones remaining

            if user.security_email_verified == True:
                return False, "Already verified.", None

            session.add(user)
            user.security_email_verified = True
            user.verify_email_code = auth

            Event.new(
                kind = "email_verified",
                session = session,
                member = user.member,
                success = True
            )

    auth.is_available = False
    session.add(auth)

    return True, None, auth


def process_project_auth_code(
    session,
    new_user,
    auth_code):
    """
    auth_code is class Auth_API object!! not string
    """

    new_user.signup_code = auth_code

    if auth_code.permission_level is not None:
        new_user.current_project_string_id = auth_code.project_string_id

        project = Project.get(session, auth_code.project_string_id)
        new_user.project_current = project

        new_user.projects.append(project)

        # We default the new user's email to being verified
        # Otherwise could be confusing to have to redeem a code twice
        new_user.security_email_verified = True

        # Do we want to record this too?
        # Could be confusing since it's a different type of code?
        # But may be good for history
        new_user.verify_email_code = auth_code

        # Do we even need this anymore?
        # UserbaseProject is not imported ...
        """
        UserbaseProject.set_working_dir(session = session, 
                                        user_id = new_user.id, 
                                        project_id = project.id, 
                                        working_dir_id = project.directory_default_id)
        """

        permission_result, permission_error = Project_permissions.add(auth_code.permission_level,
                                                                      new_user,
                                                                      auth_code.project_string_id)
