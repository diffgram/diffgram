# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.deletion import Deletion


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/update', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin"],
	apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_project_update(project_string_id): 
		
	"""
	Considerations
	1) Security
	2) Recovery
	
	* removing a user from a projects permissions effectively hides it...


	"""

	spec_list = [{'mode' : str}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400
	
	with sessionMaker.session_scope() as session:

		user = User.get(session = session)
		project = Project.get(session, project_string_id)
		
		log = project_update_core(
				session = session,
				project = project,
				mode = input['mode'],
				log = log,
				member = user.member)

		if len(log["error"].keys()) >= 1:
			return jsonify(log=log), 400

		log['success'] = True
		return jsonify(
			log=log,
			project=project.serialize()), 200



def project_update_core(session,
						project,
						mode,
						log,
						member):

	"""
	* Send email
	* Create deletion thing to track it
	* Remove permissions for all users (including Admin?)
	* Remove from project
	* Set project flag to deleted
	
	"""

	if mode == "DELETE":

		deletion = Deletion(project = project,
							member_created = member)
		session.add(deletion)
		session.add(project)

		project.deletion_pending = True

		deletion.cache = {}

		# Remove permissions for all users (including Admin?)
		for user in project.users:

			deletion.cache['permissions'] = {}

			# user_id : user permissions for project
			deletion.cache['permissions'][user.id] = user.permissions_projects[project.project_string_id]

			Project_permissions.clear_all(
				user = user,
				sub_type = project.project_string_id)

		# Remove database link to project
		project.users = [] 

		log['info']['remove'] = "Project scheduled for deletion."


		email = member.user.email

		subject = f"{project.project_string_id} scheduled for deletion."

		message = project.project_string_id + \
		" may be deleted in approximately 30 days." + \
		" Please contact us immediately if you did not authorize this change."

		communicate_via_email.send(email, subject, message)

		Event.new(
			kind = "project_delete",	
			session = session,
			member = member,
			success = True
		)


	if mode == "MAKE_PUBLIC":

		if project.is_public is True:
			log['error']['public'] = "Project already public"
			return log

		session.add(project)
		project.is_public = True

		log['info']['public'] = "Project now public."
		
		email = member.user.email

		subject = f"{project.project_string_id} now public."

		message = project.project_string_id + \
		" is now publicly accessible." + \
		" Please contact us immediately if you did not authorize this change."

		communicate_via_email.send(email, subject, message)

		Event.new(
			kind = "project_make_public",	
			session = session,
			member = member,
			success = True
			)


	if mode == "MAKE_PRIVATE":

		if project.is_public is False:
			log['error']['public'] = "Project already private"
			return log

		session.add(project)
		project.is_public = False

		log['info']['public'] = "Project now private."
		
		# Don't need to send email for making private?
		Event.new(
			kind = "project_make_private",	
			session = session,
			member = member,
			success = True
			)



	return log

