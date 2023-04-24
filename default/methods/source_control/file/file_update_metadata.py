try:
    from methods.regular.regular_api import *
    from methods.source_control.file.remove import remove_core as file_remove_core
    from methods.source_control.file.file_browser import File_Browser

except:
    from default.methods.regular.regular_api import *
    from default.methods.source_control.file.remove import remove_core as file_remove_core
    from default.methods.source_control.file.file_browser import File_Browser

from sqlalchemy.orm.session import Session
from flasgger import swag_from


@routes.route('/api/v1/project/<string:project_string_id>/file/<int:file_id>/update-metadata', methods = ['PUT'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@swag_from('../../../docs/files/file_update_metadata.yml')
def api_file_update_metadata(project_string_id: str, file_id: int):
    """
        Updates a file ID metadata.
    :param project_string_id: the project where the file belongs.
    :param file_id: the file ID to update
    :return:
    """

    spec_list = [
        {'rotation_degrees': {'type': int, 'required': False}},
        {'ordinal': {'type': int, 'required': False}}
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        member = get_member(session)
        project = Project.get(session, project_string_id)

        updated_file, log = file_update_metadata_core(
            session = session,
            project = project,
            file_id = file_id,
            rotation_degrees = input['rotation_degrees'],
            ordinal = input['ordinal'],
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        log['success'] = True
        return jsonify(log = log, file = updated_file), 200


def file_update_metadata_core(session: Session,
                              project: Project,
                              file_id: int,
                              rotation_degrees: int,
                              ordinal: int,
                              log: dict = regular_log.default()):
    file = File.get_by_id(session = session, file_id = file_id)
    if file.project_id != project.id:
        log['error']['project'] = f'File does not belong to project {project.project_string_id}'
        return None, log

    if file.type == 'image':
        if rotation_degrees is not None:
            valid_degrees = [0, 90, 180, 270]
            if rotation_degrees not in valid_degrees:
                log['error']['rotation_degrees'] = f'Invalid rotation degrees can only be {valid_degrees}'
                return None, log
            file.image.rotation_degrees = rotation_degrees
            session.add(file.image)
    if ordinal is not None:
        file.ordinal = ordinal
    session.add(file)
    result = file.serialize_with_type(session = session, regen_url = False)
    return result, log
