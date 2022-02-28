try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

import re

from shared.database.user import UserbaseProject


@routes.route('/api/v1/task/<int:task_id>/file/is_complete_toggle', 
			  methods=['POST'])
@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
def api_by_task_is_complete_toggle(task_id):
	with sessionMaker.session_scope() as session:
		task = Task.get_by_id(
					session = session,
					task_id = task_id)
		file = task.file
		new_file = file.toggle_flag_shared(session)

		if new_file is False: return jsonify(False), 400

		Event.new(					
			session = session,
			kind = "file_complete_toggle",
			member = get_member(session=session),
			project_id = task.project_id,
			file_id = file.id,
			description = f"from_task_{str(file.ann_is_complete)}"
			)

		return jsonify( success = True,
						new_file = new_file.serialize_with_type(session)), 200


@routes.route('/api/project/<string:project_string_id>' +
			  '/file/<int:file_id>/annotation/is_complete_toggle', 
			methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def ann_is_complete_toggle(project_string_id, file_id):
    """
    args
        file_id

    returns
        file (may be a new one)

    """

    # TODO review if this should be shared with file update!!!
    # probably yes!!!

    spec_list = [
        {'directory_id': int}
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        # TODO this section should maybe be it's own sub function within File?

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        directory = WorkingDir.get_with_fallback(
            session=session,
            directory_id=input['directory_id'],
            project=project)

        if directory is False:
            log['error']['directory'] = "No directory found"
            return jsonify(log=log), 400

        file = File.get_by_id_and_directory_untrusted(
            session=session,
            directory_id=directory.id,
            file_id=file_id)

        if file is None:
            return jsonify("file invalid"), 400

        new_file = file.toggle_flag_shared(session)

        if new_file is False:
            return jsonify(False), 400

        Event.new(
            session=session,
            kind="file_complete_toggle",
            member_id=user.member_id,
            project_id=project.id,
            file_id=file.id,
            description=str(file.ann_is_complete)
        )

        return jsonify(success=True,
                       new_file=new_file.serialize_with_type(session)), 200
