# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.model.model_run import ModelRun

@routes.route('/api/v1/project/<string:project_string_id>/model-runs/list', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "allow_if_project_is_public"], apis_user_list = ["api_enabled_builder"])
def model_run_list_web(project_string_id):
    """
        List all the model runs based on the given filters.
        We can filter by directory_id, id_list, file_id, job_id, status and project.
    :param project_string_id: The string ID of the project.
    :return: A JSON response containing the list of model runs or an error message.
    """
    issue_list_spec_list = [
        {"directory_id": {
            'kind': int,
            "required": False
        }},
        {"id_list": {
            'kind': list,
            "required": False
        }},
        {"file_id": {
            'kind': int,
            "required": False
        }},
        {"starts": {
            'kind': str,
            "required": False
        }},
        {"ends": {
            'kind': str,
            "required": False
        }},
        {"job_id": {
            'kind': int,
            "required": False
        }},
        {"status": {
            'kind': str,
            "required": False
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_list_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)
        if user:
            member = user.member
        else:
            if request.authorization:
                client_id = request.authorization.get('username', None)
                auth = Auth_api.get(session, client_id)
                member = auth.member

        model_run_data, log = model_run_list_core(
            session = session,
            log = log,
            project_id = project.id,
            directory_id = input['directory_id'],
            file_id = input['file_id'],
            job_id = input['job_id'],
            status = input['status'],
            starts = input['starts'],
            ends = input['ends'],
            id_list = input['id_list'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(model_run_list = model_run_data), 200


def model_run_list_core(session: object,
                    log: dict = regular_log.default(),
                    project_id: int = None,
                    directory_id: int = None,
                    file_id: int = None,
                    job_id: int = None,
                    status: str = 'open',
                    starts: str = None,
                    type: str = None,
                    ends: str = None,
                    id_list: list = None,
                    members_list: list = []):
    """
        Returns serialized dictionary of the list of model runs that match the given filters.
        This method assumes data has been validated previously, so no extra validations are done in the function.

    :param session: The database session object.
    :param log: The log dictionary.
    :param project_id: The ID of the project.
    :param directory_id: The ID of the directory.
    :param file_id: The ID of the file.
    :param job_id: The ID of the job.
    :param status: The status of the model runs.
    :param members_list: The list of members.
    :return: A tuple containing the serialized list of model runs and the log dictionary.
    """
    if project_id is None:
        log['error']['project_id'] = 'Provide project_id'
        return None, log

    model_run_list = ModelRun.list(
        session = session,
        project_id = project_id,
        starts = starts,
        ends = ends,
        id_list = id_list,


    )

    model_run_data = [run.serialize() for run in model_run_list]
    return model_run_data, log
