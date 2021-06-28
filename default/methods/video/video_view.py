from methods.regular.regular_api import *
from shared.database.task.task import Task



@routes.route('/api/project/<string:project_string_id>' +
			  '/video/single/<int:video_parent_file_id>' +
			  '/frame/<int:frame_number>', 
			  methods=['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def get_video_single_image(project_string_id, video_parent_file_id, frame_number):

	with sessionMaker.session_scope() as session:

		project = Project.get(session, project_string_id)	

		video_file = File.get_by_id_and_project(
			session= session,
			project_id = project.id,
			file_id = video_parent_file_id,
			directory_id = project.directory_default_id		# migration
			)
		if video_file is None:
			return jsonify("bad video_parent_file_id id"), 400

		return get_url_response(
			session = session,
			video_file = video_file,
			frame_number = frame_number)



@routes.route('/api/v1/task/<int:task_id>/video/single/<int:video_parent_file_id>/frame-list/', 
			  methods=['POST'], defaults={'project_string_id': None})		# CAUTION note this is swapped, we fill default of route NOT using
@routes.route('/api/project/<string:project_string_id>/video/single/<int:video_parent_file_id>/frame-list/',
			  methods=['POST'],  defaults={'task_id': -1})
@PermissionTaskOrProject.by_task_or_project_wrapper(
    apis_user_list = ["builder_or_trainer"],
    roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def get_video_image_list(project_string_id, task_id, video_parent_file_id):

	spec_list = [{"frame_list" : {
					'kind': list,
					'required': True
					}
				}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400

	with sessionMaker.session_scope() as session:

		# A little security measure 
		if len(input['frame_list']) > 100:
			return jsonify("Max 100 frames at a time"), 400

		if task_id != -1:
			task = Task.get_by_id(
				session = session,
				task_id = task_id)

			if task.file is None:
				return jsonify("Task has no video file associated."), 400
			else:
				video_file = task.file

		else:
			project = Project.get(session, project_string_id)

			video_file = File.get_by_id_and_project(
				session= session,
				project_id = project.id,
				file_id = video_parent_file_id,
				directory_id = project.directory_default_id		# migration
				)

			if video_file is None:
				return jsonify("bad video_parent_file_id id"), 400

		return get_url_for_frame_list_response(
			session = session,
			video_file = video_file,
			frame_list = input['frame_list'])


def get_url_for_frame_list_response(
		session,
		video_file,
		frame_list: list) -> list:
	"""
	"""
	url_list = []
	if video_file.video.root_blob_path_to_frames:
		for frame_number in frame_list:
			url = video_file.video.get_frame_url(frame_number = frame_number)
			url_list.append({'frame_number': frame_number, 'url': url})

	if not url_list:
		return jsonify("frame url_list failed"), 400

	return jsonify(url_list = url_list), 200


def get_url_response(
		session,
		video_file, 
		frame_number: int) -> str:
	"""
	"""
	url = None

	if video_file.video.root_blob_path_to_frames:
		url = video_file.video.get_frame_url(frame_number = frame_number)

	if url is None:
		return jsonify("frame url failed"), 400

	return jsonify(url = url), 200
