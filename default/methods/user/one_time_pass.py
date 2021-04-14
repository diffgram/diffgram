# OPENCORE - ADD
import time
import pyotp
from shared.helpers.permissions import setSecureCookie
import base64

from methods import routes
from flask import request
from flask import jsonify

from shared.database.user import User

import logging, json

from shared.helpers import sessionMaker

from shared.helpers.permissions import setSecureCookie

from shared.settings import settings



class OneTimePass():
	def new(session, user):


		secret = pyotp.random_base32()
		user.otp_secret = secret
		user.otp_enabled = True

		backup_code_list = []
		for i in range(3):		
			backup_code = pyotp.random_base32()
			backup_code_list.append(backup_code)
			user.otp_backup[backup_code] = True

		session.add(user)

		totp = pyotp.TOTP(secret)	
		otp = totp.now()
	
		qr_code_url = totp.provisioning_uri(
							user.email, 
							issuer_name="Diffgram")

		return otp, qr_code_url, backup_code_list



	def verify_otp(user, proposed_otp_code):

		totp = pyotp.TOTP(user.otp_secret)
		result = totp.verify(proposed_otp_code)

		return result


	def verify_backup_code(user, proposed_backup_code):


		result = user.otp_backup.get(proposed_backup_code, None)
		if result is None or result is False:
			return False
		else:
			# Redeem code
			user.otp_backup[proposed_backup_code] = False
			session.add(user)
			return True
	


@routes.route('/api/user/otp/enable', methods=['POST'])
def enable_otp_from_web():

	with sessionMaker.session_scope() as session:
		
		user = User.get(session)

		if not user:
			return "no user", 400, {'ContentType':'application/json'}

		otp, qr_code_url, backup_code_list = OneTimePass.new(session, user)

		out = jsonify(	success = True,
						otp = otp,
						qr_code_url = qr_code_url,
						backup_code_list = backup_code_list,
						user=user.serialize())

		return out, 200, {'ContentType':'application/json'}


@routes.route('/api/user/otp/disable', methods=['POST'])
def disable_otp_from_web():

	with sessionMaker.session_scope() as session:
		
		user = User.get(session)

		if not user:
			return "no user", 400, {'ContentType':'application/json'}

		session.add(user)

		user.otp_enabled = False
		
		out = jsonify(	success = True,
						user=user.serialize())

		return out, 200, {'ContentType':'application/json'}


@routes.route('/api/user/otp/verify', methods=['POST'])
def verify_otp_from_web():

	with sessionMaker.session_scope() as session:

		data = request.get_json(force=True)

		proposed_otp_code = data.get('otp', None)
		otp_current_session = data.get('otp_current_session', None)
		email = data.get('email', None)

		user = User.get_by_email(session, email)
		if user is None:
			return jsonify(error="No user"), 200, {'ContentType':'application/json'}

		if user.otp_current_session_expiry <= time.time():
			User.new_login_history(	session=session,
									success=False,
									otp_success=False,
									remote_address=request.remote_addr,
									user_id=user.id)
			return jsonify(error="Please login again, session expired"), 200, {'ContentType':'application/json'}

		if user.otp_current_session != otp_current_session:
			User.new_login_history(	session=session,
									success=False,
									otp_success=False,
									remote_address=request.remote_addr,
									user_id=user.id)
			return jsonify(error="Please login again, session invalid"), 200, {'ContentType':'application/json'}


		if OneTimePass.verify_otp(user, proposed_otp_code) is True:

			User.new_login_history(	session=session,
									success=True,
									otp_success=True,
									remote_address=request.remote_addr,
									user_id=user.id)

			setSecureCookie(user)

			return jsonify(user=user.serialize(), success = True), 200, {'ContentType':'application/json'}


		return jsonify(error="Invalid code"), 200, {'ContentType':'application/json'}