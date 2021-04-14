# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from shared.database.task.job.user_to_job import User_To_Job

from werkzeug.exceptions import Forbidden


@routes.route('/api/v1/job/<int:job_id>/trainer/info',
			  methods = ['GET'])
@Job_permissions.by_job_id(
	mode="trainer",
    apis_user_list = ['builder_or_trainer'])
def job_trainer_info_api(job_id):
	"""
	Basic information for job

	Labels and guides come from task

	But things like name, what type of job it is, etc...
	Other stuff can come from here
	"""
	
	log = regular_input.regular_log.default_api_log()

	with sessionMaker.session_scope() as session:

		job = Job.get_by_id(session, job_id)

		user = User.get(session)

		job_serialized = job.serialize_trainer_info_default(session = session,
															user_id = user.id)

		log['success'] = True
		return jsonify( log = log,
						job = job_serialized), 200


# TODO job permissions
# The permissions thing here was complicated because this is the 
# general info before the trainer is actually on the job.
# Also keep in mind this is showing only the title / very general info
# on the job. Still should be protected.


@routes.route('/api/v1/job/<int:job_id>/trainer/info/start',
			  methods = ['GET'])
@limiter.limit("100 per day")
def job_trainer_info_start_api(job_id):
	"""
	Starting trainer job
	"""
	
	log = regular_input.regular_log.default_api_log()

	with sessionMaker.session_scope() as session:

		job = Job.get_by_id(session, job_id)

		user = User.get(session)

		# This is only showing a user's own stuff right...

		job_serialized = job.serialize_trainer_info_default(
			session = session,
			user_id = user.id)

		log['success'] = True
		return jsonify( log = log,
						job = job_serialized), 200
