# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.task.guide import Guide
from shared.permissions.general import General_permissions


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/guide/edit', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def guide_edit_api(project_string_id): 
	"""
	Permissions checked by guide being in project.

	"""

	with sessionMaker.session_scope() as session:
		
		spec_list = [{"name" : str}, 
					 {"description_markdown": str},
					 {"id": int},
					 {"mode": str}	# defaults to UPDATE
					 ]

		log, input, untrusted_input = regular_input.master(request=request,
														   spec_list=spec_list)
		if len(log["error"].keys()) >= 1:
			return jsonify(log=log), 400

		with sessionMaker.session_scope() as session:

			guide = session.query(Guide).filter(
				Guide.id == input['id']).first()

			if guide is None:
				log["error"]["id"] = "Bad ID"
				return jsonify(log=log), 400
			
			if guide.project.project_string_id != project_string_id:
				log["error"]["id"] = "Permissions Issue - Bad ID"
				return jsonify(log=log), 400

			# Guide itself is stored as part of session
			# so don't need to return.
			guide_update_core(
					session = session,
					guide = guide,
					mode = input['mode'],
					name = input['name'],
					description_markdown = input['description_markdown']
					)

			return jsonify(log = log,
						   guide = guide.serialize_for_list_view()), 200


def guide_update_core(
		session,
		guide,
		mode,
		name,
		description_markdown):

	# Default
	if mode is None or mode == "UPDATE":

		guide.history_cache = {
			'time_updated': str(guide.time_updated),	 
			'member_updated_id': guide.member_updated_id,
			'name': guide.name,
			'description_markdown': guide.description_markdown
			}

		guide.description_markdown = description_markdown
		guide.name = name

		member = get_member(session = session)
		guide.member_updated = member

		session.add(guide)


	if mode == "ARCHIVE":
		
		guide.archived = True
		session.add(guide)




