try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.auth.member import Member
from shared.database.project import Project
from sqlalchemy.orm.session import Session


@routes.route('/api/project/<string:project_string_id>/file/<int:file_id>/get-signed-url', methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_file_get_signed_url(project_string_id, file_id):
    """
           List all the comments of the given discussion_id

       :param project_string_id:
       :param discussion_id:
       :return:
       """
    # For now, no filters needed. But might add in the future.
    log = regular_log.default()

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        file_data, log = get_file_signed_url_core(
            session = session,
            log = log,
            project = project,
            member = member,
            file_id = file_id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(file = file_data, log = log), 200


def get_file_signed_url_core(session: Session,
                             project: Project,
                             file_id: int,
                             member: Member,
                             log: dict = regular_log.default()):
    """
        List comments of the discussion. At this point we assume data has been validated so no extra checks are
        done to the input data.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """

    file = File.get_by_id(session = session, file_id = file_id)
    if file.project_id != project.id:
        log['error']['file_id'] = 'File does not belong to project'
        return None, log
    file_data = {
        'type': file.type
    }
    if file.type == "image":
        if file.image:
            file_data[file.type] = file.image.serialize_for_source_control(session = session,
                                                                           connection_id = file.connection_id,
                                                                           bucket_name = file.bucket_name,
                                                                           reference_file = file,
                                                                           regen_url = True
                                                                           )
    elif file.type == "video":
        if file.video:
            file_data[file.type] = file.video.serialize_list_view(session = session,
                                                                  project = file.project,
                                                                  connection_id = file.connection_id,
                                                                  bucket_name = file.bucket_name)
    elif file.type == "text":
        if file.text_file:
            file_data[file.type] = file.text_file.serialize(session = session,
                                                            connection_id = file.connection_id,
                                                            bucket_name = file.bucket_name,
                                                            regen_url = True
                                                            )

    elif file.type == "geospatial":
        file_data[file.type] = {
            'layers': file.serialize_geospatial_assets(session = session,
                                                       connection_id = file.connection_id,
                                                       bucket_name = file.bucket_name,
                                                       regen_url = True
                                                       )
        }
    if file.type == "audio":
        if file.audio_file:
            file_data[file.type] = file.audio_file.serialize(session = session,
                                                             connection_id = file.connection_id,
                                                             bucket_name = file.bucket_name,
                                                             regen_url = True
                                                             )

    elif file.type == "sensor_fusion":
        point_cloud_file = file.get_child_point_cloud_file(session = session)
        if point_cloud_file and point_cloud_file.point_cloud:
            file_data['point_cloud'] = point_cloud_file.point_cloud.serialize(session = session,
                                                                              connection_id = file.connection_id,
                                                                              bucket_name = file.bucket_name,
                                                                              regen_url = True
                                                                              )
    
    return file_data, log
