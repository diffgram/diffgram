from methods.regular.regular_api import *
from shared.database.action.action import Action
from shared.regular.regular_log import log_has_error
from flasgger import swag_from

@routes.route('/api/v1/project/<string:project_string_id>/action/previous/<string:action_id>', methods=['GET'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@swag_from('../../docs/actions/action_previous.yml')
def api_action_previous(project_string_id, action_id):

    with sessionMaker.session_scope() as session:
        log = regular_log.default()

        project = Project.get(session, project_string_id)
        action = Action.get_by_id(session = session, id = action_id, project_id = project.id)
        
        previous_action = action.get_previous_action(session=session).serialize()

        if log_has_error(log) >= 1:
            return jsonify(log = log), 400

        out = jsonify(previous_action=previous_action, log=log)
        return out, 200