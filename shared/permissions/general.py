# OPENCORE - ADD
from functools import wraps

from shared.database.user import User

from werkzeug.exceptions import Forbidden
from shared.helpers.permissions import getUserID
from shared.helpers.permissions import LoggedIn
from shared.helpers.permissions import defaultRedirect
from shared.helpers import sessionMaker
from shared.permissions.user_permissions import User_Permissions

import sys

# TODO thoughts on this vs project specific permissions
# (Project specific permissions requires keywoord args from function)...
# ie refactor into Roles, type or something?

# Also TODO should this be sub class of User method???

sub_type = "general"


class General_permissions():

	def grant_permission_for(Roles, 
						     apis_user_list = []):
		"""
		Defaults to forbidden if no match found

		Matching:
		1. Attempts to find match string
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

				if 'allow_anonymous' in Roles:
					return func(*args, **kwds)

				if LoggedIn() != True: 
					raise Forbidden("No access.")

				# careful as we now check additional things like 
				# api_user_list so even for "normal_users" we want to check their permissions

				with sessionMaker.session_scope() as s:
					user = s.query(User).filter(User.id == getUserID()).one()
				
					if user.is_super_admin == True:
						return func(*args, **kwds)

					User_Permissions.general(user = user,
											apis_user_list = apis_user_list)

					# Maybe other sub types in the future?
					if user.permissions_general is not None:
						for _sub_type, Permissions in user.permissions_general.items():
							#print(_sub_type, Permissions, file=sys.stderr)
							if Permissions is not None:
								if _sub_type == sub_type:
									for role in Roles:    
										#print(role, Permissions, file=sys.stderr)
										if role in Permissions:
											return func(*args, **kwds)

				raise Forbidden("No access.")     
			return inner
		return wrapper


	def remove(permission, user):
		current_permissions = user.permissions_general[sub_type]
		current_permissions.remove(permission)
		user.permissions_general[sub_type] = current_permissions


	def add(permission, user):
		current_permissions = user.permissions_general[sub_type]
		current_permissions.append(permission)
		user.permissions_general[sub_type] = current_permissions


	def clear_all(user):
		user.permissions_general[sub_type] = {}






