try:
    from methods.regular.regular_api import *
    from methods.source_control.file.remove import remove_core as file_remove_core
    from methods.source_control.file.file_browser import File_Browser

except:
    from default.methods.regular.regular_api import *
    from default.methods.source_control.file.remove import remove_core as file_remove_core
    from default.methods.source_control.file.file_browser import File_Browser

from shared.utils import job_dir_sync_utils
from shared.utils.sync_events_manager import SyncEventManager
from shared.utils.source_control.file.file_transfer_core import file_transfer_core
from shared.database.batch.batch import InputBatch


@routes.route('/api/v1/project/<string:project_string_id>/file/<int:file_id>/regenerate-cache',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_file_cache_regen(project_string_id, file_id):
    """
    For limits for this, this route may be used for single files (not just lists)

    """

    # TODO how do we want to handle this for labels?
    # I like enfocring a directory id with the request
    # But labels requires using fallback. (project default)

    spec_list = [{'frame_number': {
        "required": False,
        "kind": int
    }}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member
        project = Project.get(session, project_string_id)

        result, log = cache_regeneration_core(
            session = session,
            project = project,
            file_id = file_id,
            frame_number = input.get('frame_number'),
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        Event.new(
            session = session,
            kind = "cache_regeneration",
            member_id = member.id,
            project_id = project.id,
            file_id = file_id,
            description = str('Regenerated Cache. Frame {}'.format(input.get('frame_number')))
        )

        log['success'] = True
        return jsonify(result = result, log = log), 200


def cache_regeneration_core(session, project, file_id, frame_number, log):
    result = {}

    file = File.get_by_id(session, file_id = file_id)

    if file.project_id != project.id:
        log['error']['file_id'] = 'File {} project mismatch please provide a file within the give project: {}.'.format(
            file_id,
            project.project_string_id
        )
        return result, log

    if file.type == 'video':
        # Check that frame number exists
        if frame_number is None:
            log['error']['frame_number'] = 'File {}: provide frame number.'.format(file_id)
            return result, log
        else:
            file = session.query(File).filter(
                File.video_parent_file_id == file_id,
                File.frame_number == frame_number
            ).first()
            if not file:
                log['error']['frame_number'] = 'Frame {} does not exists.'.format(frame_number)
                return result, log

    instance_list_existing = Instance.list(session = session,
                                            file_id = file.id,
                                            limit = None)
    for instance in instance_list_existing:
        instance.hash_instance()
        session.add(instance)

    # Invalidate cache
    file.set_cache_key_dirty('instance_list')
    # Regenerate Cache
    result['file_data'] = file.get_with_cache(
        cache_key = 'instance_list',
        cache_miss_function = file.serialize_instance_list_only,
        session = session)
    result['regenerated'] = True

    return result, log
