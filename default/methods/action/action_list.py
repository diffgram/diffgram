from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.action_flow import Action_Flow
from shared.database.action.action_event import Action_Event


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_list(project_string_id):
    """

    """

    spec_list = [
        {'flow_id': int},
        {'mode': None}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        action_list = Action.list(
            session=session,
            flow_id=input['flow_id'],
            project_id=project.id,
            return_kind="objects"
        )

        action_list_serialized = []

        for action in action_list:
            action_list_serialized.append(action.serialize())

        log['success'] = True

        out = jsonify(action_list=action_list_serialized,
                      log=log)
        return out, 200


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/event/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
def api_action_event_list(project_string_id):
    """

    """

    spec_list = [
        {'flow_event_id': int},
        {'mode': None}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        event_list = Action_Event.list(
            session=session,
            id=input['flow_event_id'],
            project_id=project.id,
            limit=100,
            return_kind="objects"
        )

        event_list_serialized = []

        for event in event_list:
            event_list_serialized.append(event.serialize(
                session=session))

        log['success'] = True

        out = jsonify(event_list=event_list_serialized,
                      log=log)
        return out, 200
