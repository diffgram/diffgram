# OPENCORE - ADD
from methods.regular.regular_api import *

@routes.route('/api/v1/user/api/update', 
			  methods=['POST'])
@General_permissions.grant_permission_for(['normal_user'])
def api_enable_user():  
	"""
	Assumes for current logged in user
	Assumes user not member / auth_api
	Question is "enable" the right name when this can disbale too...

	A few context things:
		Other APIs are enabled through direct processes (generally for good reason )
		for example, "builder_api".
		In general this is more for the "optional" APIs .
		Less significant may not quite be the right word but just the concept that
		at least for now this is more for the user experience then any strict
		security / billing thing.

	"""

	spec_list = [{"api_name": str}, 
				 {"mode": {
				   'default': True,		# ENABLE (True) or DISABLE (False) ?
				   'kind': bool
				  }
				}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:

		user = User.get(session)			
		session.add(user)

		# In the future imagine we could make this a lot 
		# more generic, but for now it's a start...
		# not checking any permissions or anything here either...

		if input['api_name'] == "api_actions":

			# Can we cast this with
			# getattr(user, 'string name') ?

			user.api_actions = input['mode']

			Event.new(
				session = session,
				kind = f"api_enable_{str(input['api_name'])}",
				member_id = user.member_id,
				success = True,
				email = user.email)

			log['success'] = True

			return jsonify(log=log,
							user = user.serialize()), 200


		log['error'] = "Invalid API name"

		return jsonify(log=log), 400