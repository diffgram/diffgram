# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    print("can't import regular api (sequence.py)")
from shared.database.video.sequence import Sequence


@routes.route('/api/project/<string:project_string_id>/sequence/<int:sequence_id>/create-preview', methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def api_create_sequence_preview(project_string_id, sequence_id):
    with sessionMaker.session_scope() as session:
        log = regular_log.default()
        project = Project.get_by_string_id(session, project_string_id)
        result, log = create_sequence_preview_core(
            session = session,
            log = log,
            project = project,
            sequence_id = sequence_id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log, result = result), 400

        return jsonify(result = result, log = log), 200


def create_sequence_preview_core(session, log, project, sequence_id):
    result = {'created': False}

    sequence = Sequence.get_by_id(session, sequence_id)
    if sequence.video_file.project_id != project.id:
        log['error']['project_id'] = 'Sequence ID project mismatch'
        return result, log

    # Build preview
    instance_preview = sequence.build_instance_preview_dict(session = session)
    if instance_preview:
        result['created'] = True
    result['instance_preview'] = instance_preview
    return result, log
