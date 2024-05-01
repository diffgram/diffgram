# OPENCORE - ADD

from methods.regular.regular_api import *  # Importing methods from the regular module's regular_api

from shared.helpers.permissions import setSecureCookie  # Importing setSecureCookie from permissions helper

from shared.database.user import Signup_code  # Importing Signup_code from the user database
from shared.database.source_control.working_dir import WorkingDir  # Importing WorkingDir from source control working_dir database

from methods import routes  # Importing routes
from shared.permissions.general import General_permissions  # Importing General_permissions
from shared.permissions.project_permissions import Project_permissions  # Importing Project_permissions
from shared.communicate.email import communicate_via_email  # Importing communicate_via_email from email helper
from shared.database import hashing_functions  # Importing hashing_functions from database
from methods.user.account import account_verify  # Importing account_verify from user account methods

from methods.user.account import auth_code  # Importing auth_code from user account methods

# A long HTML template for sending a verification email
verify_email_html_template = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html> ... </html>"""


@routes.route('/api/v1/user/verify',  # Route for verifying user's email
              methods=['POST'])
@limiter.limit("3 per day")  # Limiting to 3 requests per day
def redeem_verify_via_email_api():
    """
    This function verifies a user's email using a code.
    """
    code_proposed = None
    project_string_id = None

    with sessionMaker.session_scope() as session:

        log = {}
        log['success'] = False
        log['error'] = {}

        data = request.get_json(force=True)  # Getting JSON data from the request
        email_proposed = data.get('email', None)
        auth_code_proposed = data.get('auth_code', None)

        if auth_code_proposed:
            result, message, auth = auth_code.attempt_redeem_code(session,  # Attempting to redeem the code
                                                                  auth_code_proposed,
                
