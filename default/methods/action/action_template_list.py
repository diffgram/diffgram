from methods.regular.regular_api import *
from sqlalchemy.orm.session import Session
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.action.action_template import Action_Template
from shared.database.action.action_run import ActionRun


@routes.route('/api/v1/project/<string:project_string_id>/action-template/list', methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_action_template_list(project_string_id):
    """
        Returns all the available action templates in a project.
    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        result, log = action_template_list_core(
            session = session,
            project = project,
            log = log
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        out = jsonify(action_template_list = result, log = log)
        return out, 200


def action_template_list_core(
    session: Session,
    project: Project,
    log: dict

):
    """
        Returns all available action templates for a project.
        (For now action templates are global across a diffgram installation)
    :param session:
    :return:
    """
    result = []

    templates = Action_Template.list(session)

    result = [x.serialize() for x in templates]

    return result, log
