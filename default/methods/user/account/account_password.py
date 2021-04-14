# OPENCORE - ADD
from methods.regular.regular_api import *

import re
from shared.database import hashing_functions


@routes.route('/api/v1/user/password/set', 
			  methods=['POST'])
@General_permissions.grant_permission_for(
	Roles = ['normal_user'])
@limiter.limit("3 per day") 
def user_password_set_api(): 

	spec_list = [{"password" : str}, 
			     {"password_check": str}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	if not valid_password(input['password']):
		log['error']['password'] = "Password must be between 8 and 200 characters."
		return jsonify(log=log), 400

	if input['password'] != input['password_check']:
		log['error']['password'] = "Paswords must match"
		return jsonify(log=log), 400


	with sessionMaker.session_scope() as session:

		user = User.get(session = session)

		user.password_hash = hashing_functions.make_password_hash(
				user.email, 
				input['password'])

		Event.new(
			kind = "user_set_password",	
			session = session,
			member = user.member,
			success = True
			)

		log['success'] = True
		return jsonify(log=log), 200





PASS_RE = re.compile(r"^.{8,200}$")

def valid_password(password):
	return password and PASS_RE.match(password)