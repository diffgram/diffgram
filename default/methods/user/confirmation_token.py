# OPENCORE - ADD
from flask import session as login_session

try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

try:
    from methods.user.account import auth_code
except:
    from default.methods.user.account import auth_code

from google.cloud import storage

from shared.database.user import UserLoginHistory
import logging
import sys
import re
from shared.database import hashing_functions
from shared.helpers.permissions import setSecureCookie
import pyotp
from datetime import timedelta
from flask_limiter.util import get_remote_address
from shared.helpers.security import limiter
from shared.database.user import Signup_code
from shared.settings import settings


# Testing only , returns 400 if system not in test mode

@routes.route('/api/user/confirmation-token', methods = ['GET'])
@limiter.limit("100 per hour, 1500 per day")
def get_confirmation_token_link():
    """
    
    """
    # Only allow to execute on testing modes.
    if settings.DIFFGRAM_SYSTEM_MODE not in ['testing_e2e', 'testing']:
        return jsonify(message='Invalid System Mode'), 400

    email = request.args.get('email')
    with sessionMaker.session_scope() as session:
        link_verify = Signup_code.get_latest_code(session, email = email)
        return jsonify(token = link_verify.code)
