from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.action.workflow_run import WorkflowRun
from flasgger import swag_from

# NEW
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/actions/workflow/new',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("1000 per day")
@swag_from('../../docs/actions/workflow_new.yml')
def new_workflow_factory_api(project_string_id):
    """

    Create a new flow object (defaults to "draft")
    Returns flow id to be used going forward

    """
    spec_list = [
        {'name': str},
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
        workflow = Workflow.new(
            name=input['name'],
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
        out = jsonify(workflow=workflow.serialize(),
                      log=log)
        return out, 200


# VIEW SINGLE
@routes.route('/api/v1/project/<string:project_string_id>/workflow/<int:workflow_id>',
              methods=['GET'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("1000 per day")
@swag_from('../../docs/actions/workflow_view.yml')
def workflow_view_api(project_string_id, workflow_id):
    """

    Get a single flow object based on id.
    Uses projecd id for security

    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        ### MAIN
        workflow = Workflow.get_by_id(
            session=session,
            id=workflow_id,
            project_id=project.id)
        ### END MAIN
        if workflow is None:
            log['error']['flow'] = "Invalid flow"
            return jsonify(log=log), 400

        log['success'] = True
        out = jsonify(workflow=workflow.serialize_with_actions(session = session),
                      log=log)
        return out, 200


# VIEW LIST
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/flow/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("1000 per day")
@swag_from('../../docs/actions/workflows_list.yml')
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

        flow_list = Workflow.list(
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
              '/action/workflow-run/list',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("2000 per day")
@swag_from('../../docs/actions/workflow_runs_list.yml')
def api_action_flow_event_list(project_string_id):
    """

    """

    spec_list = [
        {'flow_id': int}
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        event_list = WorkflowRun.list(
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
