# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.helpers.permissions import setSecureCookie

from shared.database.user import Signup_code
from shared.database.source_control.working_dir import WorkingDir

from methods import routes
from shared.permissions.general import General_permissions
from shared.permissions.project_permissions import Project_permissions
from shared.communicate.email import communicate_via_email
from shared.database import hashing_functions
from methods.user.account import account_verify

from methods.user.account import auth_code


@routes.route('/api/v1/user/verify', 
			  methods=['POST'])
@limiter.limit("3 per day")
def redeem_verify_via_email_api():  
	"""
	TODO clarify this is verifying an account

	"""

	code_proposed = None
	project_string_id = None

	with sessionMaker.session_scope() as session:

		log = {}
		log['success'] = False
		log['error'] = {}

		data = request.get_json(force=True)
		email_proposed = data.get('email', None)
		auth_code_proposed = data.get('auth_code', None)

		if auth_code_proposed:
			result, message, auth = auth_code.attempt_redeem_code(	session,
																	auth_code_proposed, 
																	email_proposed)
			if result == False:
				log['error']['auth_code'] = message
				return jsonify(log = log), 200

		log['success'] = True

		return jsonify(log = log), 200


#def redeem_verify_via_email_core():

@routes.route('/api/v1/user/verify/start', 
			  methods=['GET'])
@limiter.limit("2 per day")
@General_permissions.grant_permission_for(['normal_user'])
def start_verify_via_email_api():

	# TODO what other limits here??
	
	# TODO verify case of user who has multiple outstanding auth codes
	# ie is it resending same code or?

	log = regular_input.regular_log.default_api_log()

	with sessionMaker.session_scope() as session:

		user = User.get(session)

		print(user)

		result, log = start_verify_via_email( session = session, 
												user = user,
												log = log)
		if result is False:
			return jsonify(log = log), 400

	log['success'] = True
	return jsonify(log = log), 200


# TODO clarify this is verifying a "new" account
def start_verify_via_email( session, 
						    user,
							log=None):
		"""
		Goal
			Verify a user's email address is real
			Send code to email, expecting to be redeemed by 
			redeem_verify_via_email()

		Arguments
			session, db session
			user, class User() object

		Returns
			True

		"""
		if user.security_email_verified is True:
			log['error']['verify_error'] = "Already verified."
			return False, log

		result, message, auth = auth_code.new(session = session,
											 user = user,
											 email_sent_to = user.email,
											 auth_code_type = "verify_signup")

		# Autofix domains that don't end with /
		url_base = settings.URL_BASE

		if not url_base.endswith('/'):
			url_base += '/'

		link_verify = url_base + "user/account/verify_email/"+ \
						 auth.email_sent_to + \
						 "/" + \
						 auth.code


		subject = "Verify your Diffgram account now"

		message = " Verify your account now " + link_verify
		
		message += " "

		communicate_via_email.send(email = user.email, 
								   subject = subject, 
								   message = message)

		return True, log
