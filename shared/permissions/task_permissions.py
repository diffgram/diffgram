# OPENCORE - ADD
from functools import wraps

from shared.database.user import User
from shared.database.project import Project
from shared.database.auth.api import Auth_api
from shared.database.task.task import Task
from shared.database.task.job.job import Job

from werkzeug.exceptions import Forbidden
from shared.helpers.permissions import getUserID
from shared.helpers import sessionMaker

from flask import request
from shared.permissions.user_permissions import User_Permissions
from shared.permissions.project_permissions import Project_permissions


class Permission_Task():

	@staticmethod
	def by_task_id(apis_user_list):
		"""
		Defaults to forbidden if no match found

		This is just the wrapper
		"""

		def wrapper(func):
			@wraps(func)
			def inner(*args, **kwds):

				task_id = kwds.get('task_id', None)
				
				Permission_Task.by_task_id_core(task_id=task_id)

				# We expect Permission_Task to raise
				# if we get here it's allowed
				return func(*args, **kwds)

				raise Forbidden("No access.")
			return inner
		return wrapper


	@staticmethod
	def by_task_id_core(
			task_id: int,
			apis_user_list: list = ["builder_or_trainer"],
			user_id: int = None):
		"""
		returns True if valid
		"""
		
		if task_id and isinstance(task_id, int):

			with sessionMaker.session_scope() as session:

				if task_id in ["null", "undefined"]:
					raise Forbidden("No access.")

				# TODO handle for API member calls

				task = Task.get_by_id(	session = session,
										task_id = task_id)

				if task is None:
					raise Forbidden("No access.")

				# For testing we may want to pass a user id
				if not user_id: 
					user_id = getUserID()
					if user_id is None:
						raise Forbidden("Please login.")

				user = User.get_by_id(	session = session, 
										user_id = user_id)

				if user is None:
					raise Forbidden("Please login.")

				if user.is_super_admin == True:
					return True

				User_Permissions.general(user = user,
										apis_user_list = apis_user_list)


				# Over ride case

				# Job owner check
				# TODO share better with existing job permissions
				if user.api_enabled_builder is True:

					project_string_id = get_project_string_from_job_id(session, task.job_id) 

					# TODO review use of admin / editor setup here
					result = Project_permissions.check_permissions(session = session,
																	project_string_id = project_string_id,
																	Roles = ['admin', 'Editor'])

					if result is True:
						return True
					else:
						raise Forbidden("Project access invalid")

				# Default case, normal task
				if task.assignee_user == user:

					# TODO clarify why this status check is here
					if task.status in ["available", "in_progress"]:
						return True



# TODO share with job permissions

def get_project_string_from_job_id(session,
									job_id):

	job = Job.get_by_id(session, job_id)

	if job is None:
		raise Forbidden

	if job.project is None:
		raise Forbidden

	project_string_id = job.project.project_string_id

	return project_string_id