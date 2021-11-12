from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.action_flow import Action_Flow
from shared.database.action.action_flow_event import Action_Flow_Event


# NEW
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/flow/new',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("10 per day")
def new_flow_factory_api(project_string_id):
    """

    Create a new flow object (defaults to "draft")
    Returns flow id to be used going forward

    """
    spec_list = [
        {'name': str},
        {'trigger_type': str},
        {'time_window': str},
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)
        project = Project.get(session, project_string_id)

        member = user.member

        ### MAIN
        flow = Action_Flow.new(
            name=input['name'],
            trigger_type=input['trigger_type'],
            time_window=input.get('time_window', None),
            session=session,
            project=project,
            org=project.org,
            member=member)
        ### END MAIN

        Event.new(
            session=session,
            kind="new_flow",
            member=user.member,
            success=True,
            project_id=project.id,
            email=user.email
        )

        log['success'] = True
        out = jsonify(flow=flow.serialize(),
                      log=log)
        return out, 200


# VIEW SINGLE
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/flow/single',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("100 per day")
def flow_view_api(project_string_id):
    """

    Get a single flow object based on id.
    Uses projecd id for security

    """
    spec_list = [
        {'flow_id': int},
        {'mode': None}]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        ### MAIN
        flow = Action_Flow.get_by_id(
            session=session,
            id=input['flow_id'],
            project_id=project.id)
        ### END MAIN
        if flow is None:
            log['error']['flow'] = "Invalid flow"
            return jsonify(log=log), 400

        log['success'] = True
        out = jsonify(flow=flow.serialize(),
                      log=log)
        return out, 200


# VIEW LIST
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/flow/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("100 per day")
def flow_list_view_api(project_string_id):
    """

    Get a single flow object based on id.
    Uses projecd id for security

    """
    spec_list = [
        {'mode': None}]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        flow_list = Action_Flow.list(
            session=session,
            project_id=project.id,
            limit=100,
            return_kind="objects"
        )

        flow_list_serialized = []

        for flow in flow_list:
            flow_list_serialized.append(flow.serialize())

        log['success'] = True

        out = jsonify(flow_list=flow_list_serialized,
                      log=log)
        return out, 200


# EVENT LIST
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/flow/event/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_flow_event_list(project_string_id):
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

        event_list = Action_Flow_Event.list(
            session=session,
            id=input['flow_id'],
            project_id=project.id,
            limit=100,
            return_kind="objects"
        )

        event_list_serialized = []

        for event in event_list:
            event_list_serialized.append(event.serialize())

        log['success'] = True

        out = jsonify(event_list=event_list_serialized,
                      log=log)
        return out, 200
