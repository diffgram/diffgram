# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.project import ProjectStar
import re

project_name_regular_expression = re.compile(r"^[a-zA-Z0-9_ ]{4,30}$")



@routes.route('/api/project/<string:project_string_id>/update/edit', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def api_project_update_edit(project_string_id):  

	spec_list = [{'project': dict}]

	# TODO readme text should be part of project

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:

		name = input['project'].get('name', None)

		# FPS
		settings_input_video_fps = input['project'].get('settings_input_video_fps', None)

		project = session.query(Project).filter(
			Project.project_string_id == project_string_id).first()
		
		# Do we want to check values for acceptablness here too?

		# TODO review options for updating project read me
		#project.readme = text

		project.name = name
		project.settings_input_video_fps = settings_input_video_fps
	
		session.add(project)

		# need admin or editor to update this so why not serialize normal?

		log['info'] = "Update success"
		log['success'] = True
		return jsonify(log = log,
					   project = project.serialize()), 200




