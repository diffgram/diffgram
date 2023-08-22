try:
    from methods.regular.regular_api import *
    from shared.database.source_control.file_stats import FileStats
    from methods.source_control.file.remove import remove_core as file_remove_core

except:
    from default.methods.regular.regular_api import *
    from default.methods.source_control.file.remove import remove_core as file_remove_core


@routes.route('/api/v1/project/<string:project_string_id>/file/<int:file_id>/file-stats',
              methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer", "allow_if_project_is_public"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_get_file_stats(project_string_id, file_id):
    """
    For limits for this, this route may be used for single files (not just lists)

    """

    with sessionMaker.session_scope() as session:

        member = get_member(session)

        project = Project.get(session, project_string_id)
        log = regular_log.default()
        result, log = get_file_stats_core(
            session = session,
            project = project,
            file_id = file_id,
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        log['success'] = True
        return jsonify(file_stats = result, log = log), 200


def get_file_stats_core(session, project, file_id, log):
    file = File.get_by_id(session = session, file_id = file_id)
    if file.project_id != project.id:
        log['error']['project_id'] = 'Imember_created_idnvalid project ID for file'
        return None, log

    stats = FileStats.list(session = session, file_id = file_id)
    print('AAAA', stats, file_id)
    res = []

    for s in stats:
        res.append(s.serialize())
    return res, log
