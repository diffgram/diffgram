from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.action.action_run import ActionRun
from sqlalchemy.orm.session import Session
from flasgger import swag_from

@routes.route('/api/v1/project/<string:project_string_id>/action/<int:action_id>/runs/list', methods = ['GET'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
@swag_from('../../docs/actions/action_run_list.yml')
def api_action_list_web(project_string_id: str, action_id: int):
    """

    :param project_string_id:
    :return:
    """
    args = request.args
    page = 0
    page_size = 50
    if args.get('page') is not None:
        page = args.get('page')
    if args.get('page_size') is not None:
        page_size = args.get('page_size')

    with sessionMaker.session_scope() as session:

        member = get_member(session)
        project = Project.get(session, project_string_id)

        action_run_list, log = action_run_list_core(
            session = session,
            log = regular_log.default(),
            action_id = action_id,
            project = project,
            page = page,
            page_size = page_size
        )
        if regular_log.log_has_error(log):
            return jsonify(log = log), 400

        log['success'] = True

        out = jsonify(action_run_list = action_run_list, log = log)
        return out, 200


def action_run_list_core(session: Session, log: dict, project: Project, action_id: int, page = 0, page_size = 25):
    action = Action.get_by_id(session, id = action_id, project_id = project.id)
    if action is None:
        msg = f'Action ID {action_id} not found, or invalid project.'
        log['error']['action_id'] = msg
        logger.error(msg)
        return None, log

    if action.project_id != project.id:
        msg = f'Action does not belong to project'
        log['error']['project_id'] = msg
        logger.error(msg)
        return None, log

    limit = page_size
    offset = page_size * page

    action_run_list = ActionRun.list_by_action_id(session = session,
                                                  action_id = action_id,
                                                  limit = limit,
                                                  offset = offset)
    if regular_log.log_has_error(log):
        return None, log
    result = []
    for run in action_run_list:
        result.append(run.serialize())

    return result, log