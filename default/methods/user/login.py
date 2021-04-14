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



@routes.route('/api/user/login', methods=['POST'])
@limiter.limit("40 per hour, 120 per day")
def login():
	"""
	Shared method for either magic link or password
	Supports one time pass (OTP)

	"""
	with sessionMaker.session_scope() as session:

		log = {}
		log['success'] = False
		log['error'] = {}

		data = request.get_json(force=True)

		mode = data.get('mode', None)
		if mode is None or len(mode) == 0:
			log['error']['mode'] = "No mode"
			return jsonify(log=log), 400

		if mode not in ["password", "magic_auth_redeem"]:
			log['error']['mode'] = "Invalid mode"
			return jsonify(log=log), 400

		# Can have either a password or magic auth link to get to next step

		# TODO abstract password method into it's own function
		if mode == "password":
			user_email_proposed = data.get('email', None)
			if user_email_proposed is None or len(user_email_proposed) == 0:
				log['error']['email'] = "No email provided"
				return jsonify(log=log), 400

			user_password_proposed = data.get('password', None)
			if user_password_proposed is None or len(user_password_proposed) == 0:
				log['error']['password'] = "No password"
				return jsonify(log=log), 400

			user_email_proposed = user_email_proposed.lower()
			user = session.query(User).filter_by(email=user_email_proposed).first()

			if user is None:
				log['error']['email'] = "Invalid email"
				return jsonify(log=log), 400

			if user.password_attempt_count >= settings.MAX_PASSWORD_ATTEMPTS_BEFORE_LOCKOUT:
				log['error']['email'] = "Please contact us to unlock account. (Too many attempts.)"
				return jsonify(log=log), 400
						
			# TODO review in context of using having not yet set a password
			# As right now the bypass errors

			# Bypass in sandbox mode.
			if settings.NAME_EQUALS_MAIN == True and \
			settings.SANDBOX_BYPASS_LOGIN == True:
				# Success case for either mode
				response, status_code = first_stage_login_success( log = log,
																   session = session, 
																   user = user)

				return response, status_code


			if user.password_hash is None:
				log['error']['password'] = "No password set. Use magic link to login."
				return jsonify(log=log), 400


			password_result = hashing_functions.valid_password( user_email_proposed, 
																user_password_proposed, 
																user.password_hash)


			if password_result is False:
				User.new_login_history(	session=session,
										success=False,
										otp_success=None,
										remote_address=request.remote_addr,
										user_id=user.id)

				log['error']['password'] = "Invalid password"
				user.password_attempt_count += 1
				session.add(user)
				return jsonify(log=log), 400


		if mode == "magic_auth_redeem":

			magic_auth_proposed = data.get('auth_code', None)
			if magic_auth_proposed is None or len(magic_auth_proposed) == 0:
				log['error']['magic'] = "No auth code"
				return jsonify(log=log), 400

			# TODO log failed attempts (may not want to use user history thing here...)
			# since we don't have email?

			result, message, auth = auth_code.attempt_redeem_code(	session = session,
																	auth_code = magic_auth_proposed)
			if result == False:
				log['error']['magic'] = message
				return jsonify(log = log), 200

			# Success for magic auth
			user = session.query(User).filter_by(email=auth.email_sent_to).first()


		# Success case for either mode
		response, status_code = first_stage_login_success( log = log,
													       session = session, 
														   user = user)

		return response, status_code



	
def first_stage_login_success( log,
							   session, 
							   user):
	"""

	Assumes initial login success
	either after magic link or password

	TODO record what mode of login it was in login history
	(ie password or magic)

	QUESTION this assumes that magic auth does not defeat two-step verification
	"""

	login_session.permanent = True  # App config has session time out (ie 10 minutes)

	User.new_login_history(	session=session,
							success=True,
							otp_success=None,
							remote_address=request.remote_addr,
							user_id=user.id)
	session.add(user)
	user.password_attempt_count = 0

	log["success"] = True

	if user.otp_enabled is True:

		user.otp_current_session = pyotp.random_base32()
		user.otp_current_session_expiry = int(time.time()) + 180

		# Passing email for use with OTP

		return jsonify( log = log,
						otp_prompt = True,
						user_email = user.email,
						otp_current_session = user.otp_current_session), 200
		

	if user.otp_enabled is None or user.otp_enabled is False:

		setSecureCookie(user)

		return jsonify(log = log,
					   user=user.serialize()), 200



