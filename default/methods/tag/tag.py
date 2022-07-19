# OPENCORE - ADD

from methods import routes
from flask import request
from flask import jsonify
from shared.database.user import User
from shared.database.project import Project
from shared.database.project import ProjectStar
from shared.database.project import Tag
import logging
import sys
import json
from shared.helpers import sessionMaker, query_val
from shared.helpers.permissions import LoggedIn, defaultRedirect, getUserID

from shared.permissions.general import General_permissions
from shared.permissions.project_permissions import Project_permissions




# LEGACY Route TBD
@routes.route('/api/project/<string:project_string_id>/tags/update', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def update_tags(project_string_id):


	"""
	Update tags to latest

	"""
	return

	have_error = False
	error_message_list = []

	with sessionMaker.session_scope() as session:

		data = request.get_json(force=True)

		tag_list = data.get('tag_list', None)

		# tag_list could be none, ie deleted all tags...

		#if tag_list is None:
			#error_message_list.append("tag list is None")
			#return jsonify(error_message_list), 400, {'ContentType' : 'application/json'}

		project = Project.get(session, project_string_id)
		
	
		print(tag_list)
		
		rebuilt_tag_list = []

		for tag in tag_list:
			if valid_tag(tag):

				name = tag.lower()
				
				#Check if tag with same name already exists
				#If so can just add that database object to
				tag_db = session.query(Tag).filter(
									Tag.name == name).first()

				if not tag_db:

					tag_db = Tag()
					tag_db.name = name

					tag_db.is_public = project.is_public

					session.add(tag_db)

				if tag_db:
					session.add(tag_db)

				# TODO handle counts properly ie on tag being removed etc.
				#tag_db.count += 1

				rebuilt_tag_list.append(tag_db)

		session.add(project)
			

		# This handles removing link to tag that's no longer in project

		project.tag_list = rebuilt_tag_list
		

	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}



@routes.route('/api/project/<string:project_string_id>/tags/list', 
			  methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def tag_view_by_project(project_string_id):        

	with sessionMaker.session_scope() as session:

		project = Project.get_project(session, project_string_id)
		
		tag_list = Tag.get_by_project(project_id = project.id)

		tag_list_serailized = []
		for tag in tag_list:
		    tag_list_serailized.append(tag.serialize())

		out = jsonify(	success=True,
						tag_list=tag_list_serailized)

		return out, 200, {'ContentType':'application/json'}

