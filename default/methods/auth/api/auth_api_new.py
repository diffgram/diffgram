# OPENCORE - ADD
import random
import string

from methods.regular.regular_api import *

from shared.database import hashing_functions

from shared.database.auth.api import Auth_api
from shared.database.auth.member import Member


@routes.route('/api/v1/project/<string:project_string_id>/auth/api/new',
			  methods=['POST'])
@Project_permissions.user_has_project(["admin"])
def auth_api_credential_new_from_api(project_string_id):
	"""
	Endpoint to provision a new API key

	Arguments
		project_string_id, String

	Returns
		jsonify() response
			log
			if successful, auth credentials
	"""

	spec_list = [{'permission_level': str},
				 {'is_live': bool}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	if input['permission_level'] not in ["Editor", "Viewer"]:
		log["errors"]["permission_level"] = "permission_level invalid"
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:
		
		### Main
		auth = create(
			session, 
			project_string_id, 
			input['permission_level'],
			input['is_live']
			)

		log["success"] = True
		return jsonify(log=log,
				auth=auth.serialize_with_secret()), 200



def create(session, 
		   project_string_id, 
		   permission_level, 
		   is_live):
	"""
	Creates new Auth_api object

	Arguments:
		session, db object
		project_string_id, string
		permission_level, string
		is_live, bool

	Returns:
		Auth object
	"""

	auth = Auth_api()
	session.add(auth)

	member = Member()
	session.add(member)
	member.kind = "api"

	session.flush()

	member.auth_api = auth
	auth.member_id = member.id

	auth.permission_level = permission_level
	auth.project_string_id = project_string_id
	auth.is_live = is_live

	auth = create_client_auth_pair(auth)

	project = Project.get(session, project_string_id)
	auth.project_id = project.id
	
	# Careful we are placing this in the member not the auth
	# for now...

	user = User.get(session = session)

	# Careful! this is the user created not the new member()
	Event.new(
		session = session,
		kind = "new_api_auth",
		member_id = user.member_id,
		success = True,
		project_id = project.id,
		email = user.email
		)	

	return auth


def create_client_auth_pair(auth):
	"""
	Random id / secret creation and adding to Auth object

	Caution:
		Assumes auth.is_live is set

	Arguments
		Auth, Auth_api object

	Returns
		Auth, Auth_api object
	"""

	# For simplicity also include the string
	# Right in name

	if auth.is_live == True:
		auth.client_id = "LIVE__"
	else:
		auth.client_id = "TEST__"



	auth.client_id += create_random_string(length=20)
	auth.client_secret = create_random_string(length=60)

	return auth


def create_random_string(length):
	return ''.join(random.choice(string.ascii_lowercase + \
				string.digits) for x in range(length))