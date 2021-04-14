# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.project import Project

from shared.database.user import User
from shared.database.user import UserbaseProject

from shared.database.task.job.job import Job
from shared.database.task.task import Task

from methods.source_control import working_dir  # rename new to directory in the future


# Based on user being attached to job right?

# TODO do we want a seperate route
# For builders doing internal jobs? / how we want to handle that
# Still want to use most of the provisioning system

@routes.route('/api/v1/job/<int:job_id>' +
			  '/task/trainer/request',
			  methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
@Job_permissions.by_job_id(	
	mode = "trainer",
    apis_user_list = ['builder_or_trainer', 'security_email_verified'])
def task_trainer_request_api(job_id):
	"""

	"""
	log = regular_input.regular_log.default_api_log()

	with sessionMaker.session_scope() as session:

		# Job id will have already been checked in permissions
		job = Job.get_by_id(session, job_id)

		### MAIN
		user = User.get(session)
		member = user.member
		
		result, task = task_trainer_request( session = session,
											 user = user,
											 job = job)
		####

		if result is True:
			task_serialized = task.serialize_trainer_annotate(session)

			log['success'] = True
			return jsonify( log = log,
						   task = task_serialized), 200

		# TODO front end handling on this
		log['error']['task_request'] = "No tasks available."
		return jsonify( log = log), 200



def task_trainer_request(session,
						 user,
						 job):
	"""
	
	1) Check if user has any existing tasks
	2) If not, assign a new task

	ASSUMPTIONS
		Tasks are generally pre assigned

	"""

	last_task = user.last_task

	if last_task:

		# Caution, if we don't check for job id too here
		# Then run risk of task being shown not being in context of job!
		# TODO, maybe save last task in user_to_job table so it's unique per job

		if last_task.status == "available" and last_task.job_id == job.id:
			return True, last_task
	

	task = recursively_get_next_available(session = session,
										  job = job,
										  user = user)

	if task:
		# handle assigning to user and related
		task.assignee_user = user

		# TODO [ ] check prior annotation assignment thing for ideas on that

		# assign last_task to user too
		session.add(user)
		user.last_task = task


		return True, task


	return False, None


def recursively_get_next_available(session,
								   job,
								   user):
	"""
	Goal, give consideration to task types,
	and not expect that first result from shared.database
	matches "business?" logic

	Example of saying a person can't review their own task

	"""

	ignore_task_IDS_list = []

	while True:

		task = Task.get_next_available_task_by_job_id( 
			session = session,
			job_id = job.id,
			ignore_task_IDS_list = ignore_task_IDS_list)

		if task is None:
			return None

		if task.task_type == 'draw':
			return task

		if task.task_type == 'review':

			result = valid_review_task_for_user(session = session,
												task = task,
												user = user)

			if result is True:
				return task

			else:
				ignore_task_IDS_list.append(task.id)


def valid_review_task_for_user(session,
							   task,
							   user):

	parent = Task.get_by_id(session, task.parent_id)
	# task.parent not working for some reason

	if parent:
		if user == parent.assignee_user:
			return False
	
	return True