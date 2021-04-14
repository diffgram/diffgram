from methods.regular.regular_api import *
from shared.database.attribute.attribute_template_group import Attribute_Template_Group


# NEW
@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/attribute/group/new',
			  methods = ['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor"], 
	apis_user_list=["api_enabled_builder"])
@limiter.limit("10 per day")
def new_attribute_template_group_factory_api(project_string_id):
	"""

	Create and returns id to be used for Attribute Templates

	"""

	spec_list = []

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:

		user = User.get(session)
		project = Project.get(session, project_string_id)

		member = user.member

		### MAIN
		attribute_template_group = Attribute_Template_Group.new(
			session = session,
			project = project,
			member = member)
		### END MAIN

		Event.new(			
			session = session,
			kind = "new_attribute_template_group",
			member = user.member,
			success = True,
			project_id = project.id,
			email = user.email
			)

		log['success'] = True
		out = jsonify(  
			attribute_template_group = attribute_template_group.serialize(),
			log = log)

		return out, 200
