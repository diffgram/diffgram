# OPENCORE - ADD
from methods.regular.regular_api import *

import re

from shared.helpers.security import limiter

from shared.permissions.general import General_permissions
from shared.communicate.email import communicate_via_email
from shared.database import hashing_functions
from methods.user.account import account_verify


@routes.route('/api/v1/user/builder/enable', 
			  methods=['POST'])
@limiter.limit("10 per day")
@General_permissions.grant_permission_for(['normal_user'])
def builder_enable_api():  

	user_email = None

	with sessionMaker.session_scope() as session:

		log = {}
		log['success'] = False
		log['error'] = {}

		data = request.get_json(force=True)   # Force = true if not set as application/json' 

		user = User.get(session)

		# TODO test mode to disable this check

		#if user.api_enabled_builder is True:
		#	log['error']['general'] = "Already enabled."
		#	return jsonify(log = log), 200

		first_name = data.get('first_name', None)
		last_name = data.get('last_name', None)
		#phone_number = data.get('phone_number', None)
		how_hear_about_us = data.get('how_hear_about_us', None)
		city = data.get('city', None)
		company = data.get('company', None)
		how_many_data_labelers = data.get('how_many_data_labelers')

		# TODO shared validation with update / edit methods
		#if not account_edit.valid_name()

		if not first_name:
			log['error']['first_name'] = "Please provide your first name"
			
		if not last_name:
			log['error']['last_name'] = "Please provide your last name"
			
		#if not phone_number:
		#	log['error']['phone_number'] = "Please provide your phone number"

		if not city:
			log['error']['city'] = "Please provide your city"

		if not company:
			log['error']['company'] = "Please provide your company name"

		if not first_name or not last_name or not city or not company:
			return jsonify(log = log), 200


		# TODO validation
		
		session.add(user)

		# User update
		user.first_name = first_name
		user.last_name = last_name
		#user.phone_number = phone_number
		user.how_hear_about_us = how_hear_about_us
		user.city = city
		user.company_name = company
		user.signup_role = data.get('role', None)
		user.signup_demo = data.get('demo', None)
		user.signup_how_many_data_labelers = how_many_data_labelers

		#### MAIN
		result = builder_enable_core(session=session,
									 user=user)
		####

		log['success'] = True

		return jsonify(log=log,
						user = user.serialize()), 200



def builder_enable_core(session,
						user):
	"""
	Goals:
		

	Arguments:
		session, db session object
		user, class User() object

	Returns:

	"""

	# TODO check if user is already a builder
	# TODO handling if "banned" or other disables?

	user.api_enabled_builder = True
	user.last_builder_or_trainer_mode = "builder"

	Event.new(
		session = session,
		kind = "builder_api_enabled",
		member_id = user.member_id,
		success = True,
		email = user.email
	)

	# We have updated user information
	# So rerun identify.
	Event.identify_user(user)

	try:
		email_about_demo_interest(user)
	except Exception as e:
		print("email_about_demo_interest", e)

	return True
