from methods.regular.regular_api import *
from sqlalchemy.orm.session import Session
from shared.database.project import Project
from shared.database.action.action_template import Action_Template
from shared.regular.regular_log import log_has_error
from flasgger import swag_from

@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action-template/<string:action_template_id>',
              methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
@swag_from('../../docs/actions/action_template_get.yml')
def api_get_action_template(project_string_id, action_template_id):
    """
        Fetch single action template
    :param project_string_id:
    :param action_template_id:
    :return:
    """
    with sessionMaker.session_scope() as session:
        log = regular_log.default()
        project = Project.get(session, project_string_id)
        action_template, log = get_action_template_core(
            session = session,
            project = project,
            action_template_id = action_template_id,
            log = log
        )
        if log_has_error(log) >= 1:
            return jsonify(log = log), 400

        out = jsonify(action_template = action_template,
                      log = log)
        return out, 200


def get_action_template_core(session: Session,
                             project: Project,
                             action_template_id: int,
                             log: dict) -> [dict, dict]:
    action_template = Action_Template.get_by_id(session = session, id = action_template_id)

    if action_template is None:
        log['error']['action_template'] = 'Action template ID not found.'
        return None, log

    result = action_template.serialize()
    return result, log
