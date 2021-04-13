from methods.regular.regular_api import *
from shared.database.input import Input


@routes.route('/api/walrus/v1/project/<string:project_string_id>' +
              '/input/view/<int:input_id>',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def input_view_detail_api(project_string_id, input_id):
    """

    Show last x number??

    Assumption of showing project wide input?

    Status filter context:
        Better input filtering for debugging / understanding system behavior.
        And for users for larger projects, once there's 100s of inputs a person may only want to see the most recent processing ones, or confirm no failed ones etc...


    """

    log = regular_log.default()


    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        # MAIN
        input_serialized, log = input_detail_core(
            session = session,
            project = project,
            input_id = input_id,
            log=log,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

    out = jsonify(success = True,
                  input = input_serialized)
    return out, 200


def input_detail_core(
        session,
        project: Project,
        input_id: int,
        log: dict):
    """
        TODO put as part of Input class
    """

    input = Input.get_by_id(session, id = input_id)
    if input.project_id != project.id:
        log['error']['project_id'] = 'Input and project ID mismatch'
        return False, log
    return input.serialize_with_frame_packet(), log