
from methods.regular.regular_api import *

from shared.database import hashing_functions

from shared.database.auth.api import Auth_api


@routes.route('/api/v1/project/<string:project_string_id>/auth/api/revoke',
			  methods=['POST'])
@Project_permissions.user_has_project(["admin"])
def web(project_string_id):
	"""
	Endpoint to revoke an existing API key

	Arguments
		project_string_id, String

	Returns
		jsonify() response
			log
	"""

	log = {"success" : False, "errors" : []}

	data = request.get_json(force=True)

	client_id = data.get('client_id', None)
	if client_id is None:
		log["errors"].append("client_id not supplied")
		return jsonify(log), 200

	with sessionMaker.session_scope() as session:

		### Main
		revoke_result = by_client_id(session, project_string_id, client_id)

		if revoke_result is True:
			log["success"] = True

		if revoke_result is False:
			log["success"] = False

		return jsonify(log)


def by_client_id(session, project_string_id, client_id):
	"""
	This is not designed as a toggle, 
	so if auth is already False, it returns False to indicate there was no change
	"""

	auth = Auth_api.get(session, client_id)

	if auth is None:
		return False

	if auth.is_valid == False:
		return False

	auth.is_valid = False
	session.add(auth)

	return True