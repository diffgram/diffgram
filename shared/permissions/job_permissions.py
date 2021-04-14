# OPENCORE - ADD
from functools import wraps

from shared.database.user import User
from shared.database.project import Project
from shared.database.auth.api import Auth_api
from shared.database.task.job.job import Job
from shared.database.task.job.user_to_job import User_To_Job

from werkzeug.exceptions import Forbidden
from shared.helpers.permissions import getUserID
from shared.helpers.permissions import LoggedIn
from shared.helpers.permissions import defaultRedirect
from shared.helpers import sessionMaker

from flask import request
from shared.permissions.project_permissions import Project_permissions
from shared.permissions.api_permissions import API_Permissions
from shared.permissions.user_permissions import User_Permissions


class Job_permissions():
	def by_job_id(project_role_list = ["Editor", "admin"],
				  apis_project_list=[],
			      apis_user_list=[],
				  mode="builder"):
		"""
		mode == "builder":
			project_role_list required
			
		"""
		if not isinstance(project_role_list, list): project_role_list = [project_role_list]

		def wrapper(func):
			@wraps(func)
			def inner(*args, **kwds):

				job_id = kwds.get('job_id', None)
				if job_id is None or job_id == "null" or job_id == "undefined":
					raise Forbidden("job_id is invalid")

				with sessionMaker.session_scope() as session:

					# Permissions cascading from project
					project_string_id = get_project_string_from_job_id(session, job_id)


					# API
					if request.authorization is not None:

						result = API_Permissions.by_project(session = session,
															project_string_id = project_string_id,
															Roles = project_role_list)
						if result is True:
							return func(*args, **kwds)
						else:
							raise Forbidden("API access invalid")
						
					# TODO do we need to validate user has applicable mode?
					# ie they pass mode builder but are trainer?
					# Basics should fail on project level check anyway here...

					# User
					# TODO move login stuff into the general User_Permissions
					if LoggedIn() != True:
						raise Forbidden("Login again.")

					user = session.query(User).filter(User.id == getUserID()).first()

					if user is None:
						raise Forbidden("Login again.")

					# Want to use the builder API permissions instead of 
					# flags since a user may be testing this as a builder
					# TODO deprecate 'mode' flag or have it as something else
					# like "builder_only" or something 


					# Jan 3, 2020
					# One downside of doing it this way is it means
					# that we need to be careful with 
					# project_role_list list...

					if user.api_enabled_builder is True:
						result = Project_permissions.check_permissions(
							session = session,
							project_string_id = project_string_id,
							Roles = project_role_list,
							apis_project_list = apis_project_list,
							apis_user_list = apis_user_list)

						if result is True:
							return func(*args, **kwds)
						else:
							raise Forbidden("Project access invalid")

					if user.api_enabled_trainer is True:

						# TODO refactor into function				

						# TODO handle "info" case of a trainer not yet 
						# on a job seeing basic stuff on active jobs...

						# We allow trainers to see
						# Basic info before they apply
						# as long as job is active...
						
						#if job.status != "active":
						#	raise Forbidden("No access.")

						User_Permissions.general(user = user,
												 apis_user_list = apis_user_list)

						user_to_job = User_To_Job.get_single_by_ids(session = session,
																	user_id = user.id,
																	job_id = job_id)
						
						# TODO other status checking on this...

						if user_to_job is None:
							raise Forbidden("No access to this job. Please apply first.")

						
						# Success case for trainer
						return func(*args, **kwds)
					
				raise Forbidden("No access.")     
			return inner
		return wrapper


	@staticmethod
	def check_job_after_project_already_valid(
		job,
		project):

		if job is None:
			raise Forbidden("No job")

		if job.project_id != project.id:
			raise Forbidden("Permission")


def get_project_string_from_job_id(session,
									job_id):

	job = Job.get_by_id(session, job_id)

	if job is None:
		raise Forbidden

	if job.project is None:
		raise Forbidden

	project_string_id = job.project.project_string_id

	return project_string_id



def trainer_default_permissions():
	pass
	# TODO move if statement stuff to here


def check_roles(Roles, Permissions):
	for role in Roles:                               
		if role in Permissions:
			return True



