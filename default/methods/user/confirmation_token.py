# OPENCORE - ADD
# Import necessary modules and libraries
from flask import session as login_session  # Flask session object for managing user sessions

try:
    from methods.regular.regular_api import *  # Regular API methods
except:
    from default.methods.regular.regular_api import *  # Fallback for default regular API methods

try:
    from methods.user.account import auth_code  # User account-related methods
except:
    from default.methods.user.account import auth_code  # Fallback for default user account methods

# Google Cloud Storage library
from google.cloud import storage

# Import shared modules
from shared.database.user import UserLoginHistory  # User login history model
import logging
import sys
import re

# Import hashing functions
from shared.database import hashing_functions

# Import permission and security-related helpers
from shared.helpers.permissions import setSecureCookie
import pyotp
from datetime import timedelta

# Import rate limiter
from flask_limiter.util import get_remote_address
from shared.helpers.security import limiter

# Import signup code model
from shared.database.user import Signup_code

# Import system settings
from shared.settings import settings


# Testing only, returns 400 if system mode is not in test mode
@routes.route('/api/user/confirmation-token', methods=['GET'])
@limiter.limit("100 per hour, 1500 per day")
def get_confirmation_token_link():
    """
    Get the confirmation token link for a given email.

    This endpoint is used for testing purposes only and will return a 400 error if the system mode is not in test mode.
    It retrieves the latest signup code for the given email and returns the token as a JSON response.

    Returns:
        A JSON response containing the confirmation token.
    """
    # Only allow to execute on testing modes.
    if settings.DIFFGRAM_SYSTEM_MODE not in ['testing_e2e', 'testing']:
        return jsonify(message='Invalid System Mode'), 400

    # Get the email from the request arguments
    email = request.args.get('email')

    # Initialize the database session
    with sessionMaker.session_scope() as session:
        # Retrieve the latest signup code for the given email
        link_verify = Signup_code.get_latest_code(session, email=email)
        # Return the JSON response containing the confirmation token
        return jsonify(token=link_verify.code)
