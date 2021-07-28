# OPENCORE - ADD
from methods.regular.regular_api import *

from google.cloud import storage
from shared.database.user import UserLoginHistory
import logging
import re
from shared.helpers.permissions import setSecureCookie
import pyotp
from datetime import datetime
from datetime import timedelta
from flask_limiter.util import get_remote_address
from methods.user.account import auth_code


@routes.route('/api/user/login/magic/start', methods = ['POST'])
@limiter.limit("10 per day")
def start_magic_login_api():
    with sessionMaker.session_scope() as session:

        log = {}
        log['success'] = False
        log['error'] = {}

        data = request.get_json(force = True)  # Force = true if not set as application/json'

        user_email_proposed = data.get('email', None)
        if user_email_proposed is None or len(user_email_proposed) == 0:
            log['error']['email'] = "No email provided"
            return jsonify(log = log), 400

        user_email_proposed = user_email_proposed.lower()
        user = session.query(User).filter_by(email = user_email_proposed).first()

        if user is None:
            log['error']['email'] = "Invalid email"
            return jsonify(log = log), 400

        # QUESTION do we want to have this here? or as a decorator?
        if user.security_disable_global is True:
            log['error']['email'] = "Please contact us to unlock account."
            return jsonify(log = log), 400

        if user.password_attempt_count >= settings.MAX_PASSWORD_ATTEMPTS_BEFORE_LOCKOUT:
            log['error']['email'] = "Please contact us to unlock account. (Too many attempts.)"
            return jsonify(log = log), 400

        ### MAIN
        auth_result, message, auth = auth_code.new(session = session,
                                                   user = user,
                                                   email_sent_to = user.email,
                                                   auth_code_type = "magic_login")
        ###
        # TODO use message var?
        if auth_result is False:
            log['error']['magic'] = "Existing attempt, check your email"
            return jsonify(log = log), 400

        ### SUCCESS
        session.add(user)
        user.password_attempt_count += 1

        email_result = send_magic_login_email(auth = auth)

        log['success'] = True
        ####

        return jsonify(log = log), 200


def send_magic_login_email(auth):
    # optional, resend code if 15 minutes has passed?

    if settings.URL_BASE.endswith('/'):
        link_verify = settings.URL_BASE + "user/login/" + auth.code
    else:
        link_verify = settings.URL_BASE + "/user/login/" + auth.code

    subject = "Magic link Diffgram"

    message = " Login now " + link_verify

    message += " Expires in 15 minutes."

    communicate_via_email.send(email = auth.email_sent_to,
                               subject = subject,
                               message = message)

    return True
