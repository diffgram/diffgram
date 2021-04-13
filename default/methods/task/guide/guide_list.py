# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.source_control.working_dir import WorkingDir

from shared.database.task.guide import Guide
from shared.database.task.job.job import Job


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/guide/list', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor", "Viewer"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def guide_list_api(project_string_id):

	spec_list = [{'metadata': dict}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)

	with sessionMaker.session_scope() as session:  
	    	
		metadata_proposed = input['metadata']

		### MAIN ###
		project = Project.get(session = session,
							  project_string_id = project_string_id)

		guide_list, metadata = guide_view_core( session = session, 
												metadata_proposed = metadata_proposed,
												project = project)
		### ###

		log['success'] = True
		return jsonify( guide_list = guide_list, 
						metadata = metadata,
						log = log), 200


def guide_view_core( session,
					metadata_proposed,
					project,
					mode="serialize",
					user=None):
		"""
		mode
			serialize is in context of web, ie serialize the resulting list
				currently defaults to this context
			objects returns the database objects, ie for auto commit

		"""

		meta = default_metadata(metadata_proposed)

		start_time = time.time()
		output_file_list = []
		limit_counter = 0

		query = session.query(Guide)
		
		meta['guide_info'] = {}

		### START FILTERS ###
		if meta["my_stuff_only"]:

			# assumes in context of user doing search not API
			user = User.get(session)
			query = query.filter(Guide.member_created == user.member)
			
		#if meta["field"]:
			# Get field id? or ...
			# WIP
			#query = query.filter(Job.field == None)
		

		query = query.filter(Guide.project == project)


		if meta['job_id'] and meta['mode'] == 'attach':
			
			job = Job.get_by_id(session = session,
								job_id = meta['job_id'])

			ignore_id_list = []

			# TODO eventually use templates

			if job.guide_default_id:
				ignore_id_list.append(job.guide_default_id)
				serialized = job.guide_default.serialize_for_list_view()
				serialized["kind"] = "default"
				meta['guide_info']['guide_default_id'] = job.guide_default_id
				output_file_list.append(serialized)

			if job.guide_review_id:
				ignore_id_list.append(job.guide_review_id)
				serialized = job.guide_review.serialize_for_list_view()
				serialized["kind"] = "review"
				meta['guide_info']['guide_review_id'] = job.guide_review_id
				output_file_list.append(serialized)
				
			if len(ignore_id_list) != 0:
				query = query.filter(Guide.id.notin_(ignore_id_list))

		# Not archived
		query = query.filter(Guide.archived == False)

		#### END FILTERS ###

		query = query.limit(meta["limit"])
		query = query.offset(meta["start_index"])
		guide_list = query.all()

		if mode == "serialize":

			for guide in guide_list:
					
				serialized = guide.serialize_for_list_view()
				output_file_list.append(serialized)
				limit_counter += 1

		meta['end_index'] = meta['start_index'] + len(guide_list)
		meta['length_current_page'] = len(output_file_list)
		
		if limit_counter == 0:
			meta['no_results_match_meta'] = True

		end_time = time.time()
		print("guide meta time", end_time - start_time)

		return output_file_list, meta


def default_metadata(meta_proposed):
	"""
	all fields needed by listed here
	"""
	
	server_side_limit = 1000  # Clarify this is limit of results returned PER PAGE , user can go to next page to see more results
	
	name = None
	field = None
	#type = None
	#status?
	
	meta = {}

	meta['limit'] = 25

	meta["start_index"] = 0

	# TODO use some kind of regular method for these key checks...
	meta["my_stuff_only"] = meta_proposed.get("my_stuff_only", None)
	meta["field"] = meta_proposed.get("field", None)
	meta["job_id"] = meta_proposed.get("job_id", None)
	meta["mode"] = meta_proposed.get("mode", None)

	"""
	# WIP WIP WIP

	#meta['name'] = meta_proposed.get("name", None)
	#meta['search_term'] = meta_proposed.get('search_term', None)
	meta_limit_proposed = meta_proposed.get('limit', None)
		
	if meta_limit_proposed:
		if meta_limit_proposed <= server_side_limit:
			meta["limit"] = meta_limit_proposed
		else:
			meta["limit"] = server_side_limit
					
	request_next_page = meta_proposed.get('request_next_page', None)

	if request_next_page is True and meta_proposed.get('previous', None):
		meta['image']["start_index"] = int(meta_proposed['previous']['image'].get('end_index', 0))
	"""

	return meta