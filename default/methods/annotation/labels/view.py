import random
import string

from flask import request
from flask import jsonify

from shared.database import hashing_functions
from methods import routes

from shared.database.project import Project
from shared.database.source_control.file import File
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.working_dir import WorkingDir

from shared.permissions.project_permissions import Project_permissions

from shared.helpers import sessionMaker



# ADDING new view functions here?
# TODO merge old view functions from labels.py



@routes.route('/api/v1/project/<string:project_string_id>' + \
			  '/labels/view/name_to_file_id', 
			  methods=['GET'])
@Project_permissions.user_has_project(
	["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def web_build_name_to_file_id_dict(project_string_id):
	"""
	Given we know a label_name, and where we are working,
	return the label_file_id

	Arguments:
		project_string_id, integer
		working_dir_id, integer

	Returns:
		dict of label files
		or None / failure case

	"""
	log = {"success" : False, "errors" : []}

	directory_id = request.headers.get('directory_id', None)
	if directory_id is None:
		log["errors"].append("'directory_id' not supplied")
		return jsonify(log), 200

	with sessionMaker.session_scope() as session:

		project = Project.get(session, project_string_id)
		verify_result = WorkingDir.verify_directory_in_project(
										session, project, directory_id)
		if verify_result is False:
			log["errors"].append("Invalid directory id")
			log["success"] = False
			return jsonify(log=log), 200

		name_to_file_id, result = build_name_to_file_id_dict(session = session, 
															directory_id = directory_id)
		if result == True:
			log["success"] = True
			
	return jsonify(log=log,
				   name_to_file_id=name_to_file_id), 200



def build_name_to_file_id_dict(session, directory_id):
	
	directory_id = int(directory_id)

	sub_query = WorkingDirFileLink.get_sub_query(session=session,
											     working_dir_id = directory_id, 
												 type="label")

	# Could also try and merge on labels or just filter through here

	file_list = session.query(File).filter(
					File.id == sub_query.c.file_id,
					File.state != "removed").all()

	out = {}

	for file in file_list:
		out[file.label.name] = file.id

	return out, True
