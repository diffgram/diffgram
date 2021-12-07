from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap


@routes.route('/api/v1/job/<int:job_id>/task/list', methods=['POST'])
@Job_permissions.by_job_id(project_role_list = ["admin", "Editor", "Viewer"], apis_user_list = ['builder_or_trainer'])
def task_list_by_job_api(job_id):
    with sessionMaker.session_scope() as session:
        spec_list = [{'date_from': None},
                     {'date_to': None},
                     {'status': None},
                     {'job_id': None},
                     {'project_string_id': None},
                     {'issues_filter': None},
                     {'project_id': {
                         'required': False,
                         'kind': int
                     }},
                     {'file_id': {
                         'required': False,
                         'kind': int
                     }},
                     {'page_number': {
                         'required': False,
                         'kind': int
                     }},
                     {'incoming_directory_id': None},
                     {'limit_count': {'required': False, 'kind': int, 'default': 25}},
                     {'mode_data': str}]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        job = Job.get_by_id(session, job_id)
        return _task_list_api(project_id=job.project.id, input=input, log=log)


@routes.route('/api/v1/project/<string:project_string_id>/task/list', methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def task_list_api(project_string_id):
    with sessionMaker.session_scope() as session:
        spec_list = [{'date_from': None},
                     {'date_to': None},
                     {'status': None},
                     {'job_id': None},
                     {'issues_filter': None},
                     {'project_string_id': None},
                     {'project_id': {
                         'required': False,
                         'kind': int
                     }},
                     {'file_id': {
                         'required': False,
                         'kind': int
                     }},
                     {'incoming_directory_id': None},
                     {'limit_count': {'required': False, 'kind': int, 'default': 25}},
                     {'mode_data': str}]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        # For now we are not supporting querying the entire file list of a project.
        # So we check we have either a job ID or a FileID to filter with
        if input['file_id'] is None and input['job_id'] is None:
            log['error']['file_id'] = 'Please Provide a file ID'
            log['error']['job_id'] = 'Please Provide a job ID'
            return jsonify(log = log), 400

        project = Project.get_by_string_id(session, project_string_id=project_string_id)
        return _task_list_api(session = session, project_id=project.id, input=input, log=log)


def _task_list_api(session, project_id, input=input, log = regular_log.default()):

        task_list = task_list_core(session=session,
                                   date_from=input['date_from'],
                                   date_to=input['date_to'],
                                   status=input['status'],
                                   job_id=input['job_id'],
                                   incoming_directory_id=input['incoming_directory_id'],
                                   project_id=project_id,
                                   file_id=input['file_id'],
                                   mode_data=input['mode_data'],
                                   issues_filter = input['issues_filter'],
                                   limit_count=input['limit_count'],
                                   page_number=input.get('page_number'))
        initial_dir_sync = None
        if input.get('job_id'):
            job = Job.get_by_id(session, input['job_id'])
            initial_dir_sync = job.pending_initial_dir_sync
            allow_reviews = job.allow_reviews
            log['success'] = True
            return jsonify(log=log,
                        task_list=task_list,
                        pending_initial_dir_sync=initial_dir_sync, allow_reviews=allow_reviews), 200

        return jsonify(log=log,
                    task_list=task_list,
                    pending_initial_dir_sync=initial_dir_sync), 200


def get_external_id_to_task(session, task, task_template):
    if not task_template:
        return
    if not task_template.interface_connection:
        return
    connection = task_template.interface_connection
    if connection.integration_name == 'labelbox':
        # Try to find the task external ID
        external_map = ExternalMap.get(
            session = session,
            task_id = task.id,
            diffgram_class_string = "task",
            type = "labelbox",
        )
        if not external_map:
            return None
        return external_map.external_id


def task_list_core(session,
                   date_from,
                   date_to,
                   status,
                   job_id,
                   incoming_directory_id,
                   project_id,
                   file_id,
                   mode_data,
                   issues_filter,
                   limit_count = 25,
                   page_number = 0):
    # if using time created

    if limit_count is None:
        limit_count = 25

    task_list = Task.list(
        session = session,
        date_from = date_from,
        date_to = date_to,
        status = status,
        job_id = job_id,
        project_id = project_id,
        file_id = file_id,
        incoming_directory_id = incoming_directory_id,
        issues_filter = issues_filter,
        limit_count=limit_count,
        page_number=page_number

    )

    out_list = []
    task_template = Job.get_by_id(session, job_id = job_id)

    for task in task_list:

        # TODO get builder vs trainer mode

        if mode_data == "exam_results":
            serialized = task.serialize_for_exam_results()
        else:
            serialized = task.serialize_for_list_view_builder(session=session)
        external_id = get_external_id_to_task(session, task, task_template)
        if external_id:
            serialized['external_id'] = external_id
        out_list.append(serialized)

    return out_list
