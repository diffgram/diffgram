# OPENCORE - ADD


class Feature_permissions():
	def user_has_project(Roles):
		"""
		Defaults to forbidden if no match found

		Arguments:
			Roles, list of strings, ie ['allow_anonymous', 'editor']
		Matching:
		1. Attempts to find match for project string
		2. If found, attempts to find match for permissions for that project
		3. If found, returns function.

		Exceptions:

		'allow_anonymous'
		user.is_super_admin
	
	   """
		if not isinstance(Roles, list): Roles = [Roles]

		def wrapper(func):
			@wraps(func)
			def inner(*args, **kwds):

				with sessionMaker.session_scope() as s:

					
					if 'allow_anonymous' in Roles:
						return func(*args, **kwds)

					# Careful here! Just becuase a project is public
					# Doesn't mean public is allowed acccess to all
					# routes. ie only admins can delete project
					if 'allow_if_project_is_public' in Roles:
						if project_string_id:
							project = Project.get(s, project_string_id)
							if project:
								if project.is_public is True:
									return func(*args, **kwds)

					if LoggedIn() != True:
						raise Forbidden("No access.")

					if 'allow_any_logged_in_user' in Roles:
						return func(*args, **kwds)

					user = s.query(User).filter(User.id == getUserID()).one()
				
					if user.is_super_admin == True:
						return func(*args, **kwds)

					# This could be slow if a user has a lot of projects?
					for project, Permissions in user.permissions_projects.items():
					
						if Permissions is None:
							continue

						if project_string_id == project:          
							check_role_result = check_roles(Roles, Permissions)
							if check_role_result is True:
								return func(*args, **kwds)


				raise Forbidden("No access.")     
			return inner
		return wrapper