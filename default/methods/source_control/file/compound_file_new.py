try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.auth.member import Member
from shared.database.project import Project
from shared.database.input import Input
from sqlalchemy.orm.session import Session


@routes.route('/api/v1/project/<string:project_string_id>/file/new-compound', methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_file_compound_new(project_string_id):
    """
        Create a new compound file.
       :param project_string_id:
       :return:
       """
    spec_list = [{'name': str},
                 {'directory_id': None}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if regular_log.log_has_error(log):
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        file_data, log = file_compound_new_core(
            session = session,
            log = log,
            project = project,
            member = member,
            directory_id = input['directory_id'],
            name = input['name'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(file = file_data, log = log), 200


def file_compound_new_core(session: Session,
                           project: Project,
                           directory_id: int,
                           name: int,
                           member: Member,
                           log: dict = regular_log.default()):
    """
        Creates a new compound file.
    :param session:
    :param project:
    :param directory_id:
    :param name:
    :param member:
    :param log:
    :return:
    """

    dataset = WorkingDir.get_by_id(session = session, directory_id = directory_id)

    if dataset.project_id != project.id:
        msg = f'Dataset {directory_id} does not belong to project {project.project_string_id}'
        log['error']['directory_id'] = msg

        return None, log
    input_obj = Input.new(
        directory_id = directory_id,
        project_id = project.id,
        project = project,
        type = 'from_compound',
        media_type = 'compound'


    )

    file = File.new(
        session = session,
        working_dir_id = directory_id,
        file_type = "compound",
        original_filename = name,
        project_id = project.id,  # TODO test if project_id is working as expected here
        input_id = input_obj.id
    )
    input_obj.file_id = file.id
    input_obj.original_filename = name
    input_obj.status = 'success'
    input_obj.percent_complete = 100
    session.add(input_obj)
    session.flush()
    file_data = file.serialize_base_file()
    file_data['input'] = input_obj.serialize()
    return file_data, log
