from methods.regular.regular_api import *

from shared.database.user import User
from shared.database.task.job.job import Job


@routes.route('/api/v1/job/<int:job_id>/builder/info',
			  methods = ['POST'])
@Job_permissions.by_job_id(
	project_role_list = ["admin", "Editor", "Viewer"],
	apis_project_list = [],
	apis_user_list=["api_enabled_builder"])
@limiter.limit("300 per day")
def job_info_builder_api(job_id):
	"""

	"""
	
	spec_list = [
		{'mode_data': None}, 	# Default of None is ok, if data, then type str
		{'refresh_stats': {
			'default': True,
			'kind': bool,
			'required': False
			}
		}
		]
	

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)

	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:

		job = Job.get_by_id(session, job_id)

		user = User.get(session = session)

		job_serialized = job_info_builder_core(session = session, 
											  job = job, 
											  user = user,
											  input = input)


		log['success'] = True
		return jsonify( log = log,
						job = job_serialized), 200


def job_info_builder_core(session, 
						  job,
						  user,
						  input 
						  ):

	if input['mode_data'] in ['job_edit']:
		job_serialized = job.serialize_builder_info_edit(session)
		return job_serialized

	# Refresh task count
	if input.get('refresh_stats') is True:
		job.refresh_stat_count_tasks(session)

	# Default case of None or in ["job_detail"]
	job_serialized = job.serialize_builder_info_default(
		session = session,
		user = user)

	return job_serialized