from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.action.action_run import ActionRun
from shared.regular.regular_log import log_has_error

@routes.route('/api/v1/project/<string:project_string_id>/action/<string:action_id>', methods=['GET'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_stat(project_string_id, action_id):

    # spec_list = []

    # log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)
    # if len(log["error"].keys()) >= 1:
    #     return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        log = regular_log.default()

        action_run_list = ActionRun.list_by_action_id(session, action_id)

        action_run_list_serialized = []

        for action_run in action_run_list:
            action_run_list_serialized.append(action_run.serialize_action_run())

        if log_has_error(log) >= 1:
            return jsonify(log = log), 400

        out = jsonify(action_list=action_run_list_serialized, log=log)
        return out, 200