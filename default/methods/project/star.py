# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.project import ProjectStar
from shared.helpers.permissions import LoggedIn, getUserID, defaultRedirect

	
@routes.route('/api/project/<string:project_string_id>/' +
			  'username/<string:username>/star/toggle', 
			  methods=['POST'])
@Project_permissions.user_has_project(["allow_if_project_is_public", 
									   "Viewer", "admin", "Editor"])
def star_project_toggle(project_string_id, username):  

	with sessionMaker.session_scope() as session:

		data = request.get_json(force=True) 

		user = User.get(session)
		if user is None:
			return jsonify(success = False), 400, {'ContentType':'application/json'}

		project = Project.get(session, project_string_id)
		if project is None:
			return jsonify(success = False), 400, {'ContentType':'application/json'}
		
		existing_star = session.query(ProjectStar).filter(
				ProjectStar.project_id == project.id,
				ProjectStar.user_id == user.id).first()
		if existing_star:

			# TODO Do we want to do a soft delete here?
			session.delete(existing_star)

			session.add(project)
			project.star_count -= 1

			return jsonify(success = True,
						   star_count = project.star_count,
						   state = "Unstarred"), 200, {'ContentType':'application/json'}


		project_star = ProjectStar()
		project_star.user = user
		project_star.project = project

		session.add(project_star)

		if project.star_count:
			project.star_count += 1
		else:
			project.star_count = 1

		session.add(project)
		
	
		return jsonify(success = True,
						star_count = project.star_count,
						state = "Starred"), 200, {'ContentType':'application/json'}


@routes.route('/api/project/<string:project_string_id>' +
			  '/star/list',  
			  methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def star_view_list(project_string_id):        

	with sessionMaker.session_scope() as session:

		project = Project.get_project(session, project_string_id)
		if project is None:
			return jsonify(success=False), 400, {'ContentType':'application/json'}
		
		user_list = project.serialize_star_list_PUBLIC()
		out = jsonify(	success=True,
						user_list=user_list)

		return out, 200, {'ContentType':'application/json'}



@routes.route('/api/project/<string:project_string_id>/' +
			  'username/<string:username>/star/status',
			 methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def star_status(project_string_id, username):        

	with sessionMaker.session_scope() as session:
		user = User.get(session)
		if user is None:
			return jsonify(success = False), 400, {'ContentType':'application/json'}

		project = Project.get(session, project_string_id)
		if project is None:
			return jsonify(success = False), 400, {'ContentType':'application/json'}
		
		star = session.query(ProjectStar).filter(
			ProjectStar.user_id == user.id,
			ProjectStar.project_id == project.id).first()

		if star is None:
			return jsonify(success=True,
						   state="Star"), 200, {'ContentType':'application/json'}
		
		if star:
			return jsonify(success=True,
						   state="Starred"), 200, {'ContentType':'application/json'}

