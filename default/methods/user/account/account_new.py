# OPENCORE - ADD
from methods.regular.regular_api import *

import re
from shared.helpers.permissions import setSecureCookie
from shared.database.user import Signup_code
from shared.database.auth.member import Member

from shared.database import hashing_functions
from methods.user.account import account_verify
from methods.user.account import auth_code  # TODO rename this / put in Auth() class
from shared.database import hashing_functions
from shared.database.account.account import Account

@routes.route('/api/v1/user/pro/new',
              methods = ['POST'])
@limiter.limit("3 per day")  # May have some errors so a few chances
def user_pro_new_api():
    spec_list = [
        {"email": {
            'kind': str,
            'required': True
        }
        },
        {"signup_code": {
            'kind': str,
            'required': False
        }
        },  # Not yet supported for Pros
        {"password": {
            'kind': str,
            'required': True
        }
        },
        {"password_check": {
            'kind': str,
            'required': True
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

    if not valid_password(input['password']):
        log['error']['password'] = "Password must be between 8 and 200 characters."
        return jsonify(log = log), 400

    if input['password'] != input['password_check']:
        log['error']['password'] = "Passwords must match"
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        email = input['email'].lower()

        log = validate_email_and_existing_from_raw(
            email = email,
            session = session,
            log = log)

        if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

        new_user = user_new_core(session = session,
                                 email = email)

        setSecureCookie(new_user)

        User.new_login_history(session = session,
                               success = True,
                               otp_success = None,
                               remote_address = request.remote_addr,
                               user_id = new_user.id)

        new_user.password_hash = hashing_functions.make_password_hash(
            new_user.email,
            input['password']
        )

        log['success'] = True

        return jsonify(log = log), 200


def validate_email_and_existing_from_raw(
    email: str,
    log: dict,
    session):
    log = validate_email_from_raw(
        email = email,
        log = log)

    if len(log["error"].keys()) >= 1:
        return log

    log = validate_existing_user_from_raw(
        email = email,
        session = session,
        log = log)

    if len(log["error"].keys()) >= 1:
        return log

    return log


def validate_email_from_raw(
    email: str,
    log: dict):
    valid_email = validate_email(email)
    if not valid_email:
        log['error']['email'] = "Invalid email"

    return log


def validate_existing_user_from_raw(
    email: str,
    session,
    log: dict):
    existing_user = session.query(User).filter_by(
        email = email).first()
    if existing_user is not None:
        log['error']['email'] = "Existing email"
        return log

    return log


@routes.route('/api/v1/user/new',
              methods = ['POST'])
@limiter.limit("500 per day")  # May have some errors so a few chances
def user_new_api():
    spec_list = [
        {"email": {
            'kind': str,
            'required': True
        }
        },
        {"signup_code": {
            'kind': str,
            'required': False
        }
        },
        {"password": {
            'kind': str,
            'required': True
        }
        },
        {"password_check": {
            'kind': str,
            'required': True
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    if not valid_password(input['password']):
        log['error']['password'] = "Password must be between 8 and 200 characters."
        return jsonify(log = log), 400

    if input['password'] != input['password_check']:
        log['error']['password'] = "Passwords must match"
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        email = input['email'].lower()

        log = validate_email_and_existing_from_raw(
            email = email,
            session = session,
            log = log)

        if len(log["error"].keys()) >= 1: return jsonify(log = log), 400

        new_user = user_new_core(session = session,
                                 email = email)

        user_signup_code = input['signup_code']

        # Since signup code is now optional still create new user???
        # The signup code knows it's type, so if say the user is being added
        # to an org it gets handled here
        ### AUTH CODE
        project_string_id = None

        if user_signup_code:
            result, message, auth = auth_code.attempt_redeem_code(
                session = session,
                auth_code = user_signup_code,
                email = new_user.email,
                new_user = new_user)

            if result == False:
                log['error']['signup_code'] = message
            # As in above, not throwing error here since signup code
            # is optional now?

            if auth:
                project_string_id = auth.project_string_id
                log['auth'] = {}
                log['auth']['type'] = auth.type

                # careful this is permission_level in signupcode/auth
                # and user_permission_level  (add 'user' in trainer org permissions)
                log['auth']['user_permission_level'] = auth.permission_level

        ### AUTH CODE end

        setSecureCookie(new_user)

        User.new_login_history(session = session,
                               success = True,
                               otp_success = None,
                               remote_address = request.remote_addr,
                               user_id = new_user.id)

        new_user.password_hash = hashing_functions.make_password_hash(
            new_user.email,
            input['password']
        )

        log['success'] = True

        return jsonify(log = log,
                       project_string_id = project_string_id,
                       user = new_user.serialize()
                       ), 200


def user_new_core(session,
                  email,
                  user_signup_code = None):
    """
    Goals:
        Blindly creates a new user and accepts signup code
        Used in context with a api that checks validity of request
        Start email verification

    Arguments:
        session, db session object
        email, string
        user_signup_code, class Auth_code (prior Signup_Code) object

    Returns:
        new_user, class User() object
        project_string_id, string project id (future maybe just return class Project() object?)

    """
    member = Member()
    session.add(member)
    member.kind = "human"

    new_user = User(email = email,
                    created_remote_address = request.remote_addr,
                    member = member
                    )

    # For Open Core Installs
    # Make the first user the super admin by default.
    user_list = session.query(User).all()
    if len(user_list) == 0:
        new_user.is_super_admin = True
        new_user.security_email_verified = True

    session.add(new_user)
    session.flush()  # Get ids (member and user)
    member.user = new_user
    new_user.member_id = member.id
    new_user.username = new_user.id

    new_user.permissions_projects = {}  # I don't like having this here but alternative of committing object seems worse

    ### VERIFY
    #	context,this is below signup code
    #	as potentially signup code effects what type of verify email we send?
    #	ie "welcome to xyz project message??"

    if new_user.is_super_admin != True:
        if settings.EMAIL_VALIDATION:
            start_verify_result, _ = account_verify.start_verify_via_email(session = session,
                                                                           user = new_user)
        else:
            new_user.security_email_verified = True

    # Routing if invited to something through signup code
    # ie a specific project / org / file
    # Sort of handled by project_string_id

    General_permissions.add('normal_user', new_user)
    session.add(new_user)

    Event.identify_user(new_user)

    Account.account_new_core(
        session = session,
        primary_user = new_user,
        mode_trainer_or_builder = "builder",
        account_type = "billing",
        nickname = "My Account")

    Event.new(
        session = session,
        kind = "new_user",
        member_id = new_user.member_id,
        success = True,
        email = new_user.email
    )

    return new_user


# Define error handling functions for user creation
# Allow a-z, A-Z, 0-0, _, - using regular expression
# 3 - 20 characters

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def validate_email(email):
    if email and EMAIL_RE.match(email):
        return True
    else:
        return False


PASS_RE = re.compile(r"^.{8,200}$")


def valid_password(password):
    return password and PASS_RE.match(password)
