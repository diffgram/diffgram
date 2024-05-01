# OPENCORE - ADD
# Import necessary modules and classes
from methods.regular.regular_api import *

from shared.database.project import ProjectStar
from shared.helpers.permissions import LoggedIn, getUserID, defaultRedirect

# Define a decorator for route and permission checks
@routes.route('/api/project/<string:project_string_id>/' +
			  'username/<string:username>/star/toggle', 
			  methods=['POST'])
@Project_permissions.user_has_project(["allow_if_project_is_public", 
									   "Viewer", "admin", "Editor"])
# Define a function to toggle star status for a project
def star_project_toggle(project_string_id, username):  

	with sessionMaker.session_scope() as session:

		# Get request data as JSON
		data = request.get_json(force=True)  

		# Get current user from session
		user = User.get(session)
		if user is None:
			# Return error if user is not found
			return jsonify(success = False), 400, {'ContentType':'application/json'}

		# Get project based on the provided string ID
		project = Project.get(session, project_string_id)
		if project is None:
			# Return error if project is not found
			return jsonify(success = False), 400, {'ContentType':'application/json'}
		
		# Check if the user has already starred the project
		existing_star = session.query(ProjectStar).filter(
				ProjectStar.project_id == project.id,
				ProjectStar.user_id == user.id).first()
		if existing_star:

			# If the user has already starred the project, remove the star
			session.delete(existing_star)

			session.add(project)
			project.star_count -= 1

			# Return success response with updated star count and state
			return jsonify(success = True,
						   star_count = project.star_count,
						   state = "Unstarred"), 200, {'ContentType':'application/json'}

		# If the user has not starred the project, create a new star
		project_star = ProjectStar()
		project_star.user = user
		project_star.project = project

		session.add(project_star)

		if project.star_count:
			project.star_count += 1
		else:
			project.star_count = 1

		session.add(project)
		
		# Return success response with updated star count and state
		return jsonify(success = True,
						star_count = project.star_count,
						state = "Starred"), 200, {'ContentType':'application/json'}


# Define a function to view the list of users who have starred a project
@routes.route('/api/project/<string:project_string_id>' +
			  '/star/list',  
			  methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def star_view_list(project_string_id):        

	with sessionMaker.session_scope() as session:

		# Get project based on the provided string ID
		project = Project.get_project(session, project_string_id)
		if project is None:
			# Return error if project is not found
			return jsonify(success=False), 400, {'ContentType':'application/json'}
		
		# Serialize and return the list of users who have starred the project
		user_list = project.serialize_star_list_PUBLIC()
		out = jsonify(	success=True,
						user_list=user_list)

		return out, 200, {'ContentType':'application/json'}


# Define a function to check the star status of a user for a project
@routes.route('/api/project/<string:project_string_id>/' +
			  'username/<string:username>/star/status',
			 methods=['GET'])
@Project_permissions.user_has_project(["allow_if_project_is_public",
									   "admin", 
									   "Editor", 
									   "Viewer"])
def star_status(project_string_id, username):        

	with sessionMaker.session_scope() as session:
		# Get current user from session
		user = User.get(session)
		if user is None:
			# Return error if user is not found
			return jsonify(success = False), 400, {'ContentType':'application/json'}

		# Get project based on the provided string ID
		project = Project.get(session, project_string_id)
		if project is None:
			# Return error if project is not found
			return jsonify(success = False), 400, {'ContentType':'application/json'}
		
		# Check if the user has starred the project and return the status
		star = session.query(ProjectStar).filter(
			ProjectStar.user_id == user.id,
			ProjectStar.project_id == project.id).first()

		if star is None:
			# Return star status if the user has not starred the project
			return jsonify(success=True,
						   state="Star"), 200, {'ContentType':'application/json'}
		
		if star:
			# Return starred status if the user has starred the project
			return jsonify(success=True,
						   state="Starred"), 200, {'ContentType':'application/json'}
