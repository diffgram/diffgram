# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.task.guide import Guide
from shared.permissions.general import General_permissions


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/guide/new', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def guide_new_api(project_string_id):  

	spec_list = [{"name" : str}, 
			     {"description_markdown": str}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:
		
		member = get_member(session = session)

		### MAIN ###
		project = Project.get(session = session,
							  project_string_id = project_string_id)

		guide = guide_new_core(session = session,
								member = member,
								name = input['name'],
								description_markdown = input['description_markdown'],
								project = project)
		### end main ###

		log['success'] = True

		# For ID
		session.flush()

		return jsonify(log = log,
					   guide = guide.serialize_for_list_view()), 200


def guide_new_core(session, 
				   member,
				   name,
				   description_markdown,
				   project):
	"""
	Create a new guide

	"""

	guide = Guide()
	session.add(guide)

	guide.member_created = member
	guide.description_markdown = description_markdown
	guide.name = name

	# optional
	guide.project = project

	# This was for silly hubspot requiring email for event...
	user_email = None
	user = member.user
	if user:
		user_email = user.email
	
	Event.new(
		kind = "new_guide",	
		session = session,
		member_id = member.id,
		success = True,
		email = user_email
		)


	return guide
