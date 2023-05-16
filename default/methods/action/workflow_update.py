from methods.regular.regular_api import *
from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from flasgger import swag_from
from shared.scheduler.job_scheduling import remove_job_scheduling, add_job_scheduling

@routes.route('/api/v1/project/<string:project_string_id>' +
              '/actions/workflow/update',
              methods = ['PUT'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("2000 per day")
@swag_from('../../docs/actions/workflow_update.yml')
def api_workflow_update(project_string_id):
    """
        Updates the given workflow.
    :param project_string_id:
    :return:
    """

    spec_list = [
        {'workflow_id': int},
        {'name': str},
        {'mode': str},
        {'active': bool}

    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        project = Project.get(session, project_string_id)

        workflow = Workflow.get_by_id(
            session = session,
            id = input['workflow_id'],
            project_id = project.id)

        if workflow is None:
            log['error']['flow'] = "No Flow found"
            return jsonify(log = log), 400

        log = flow_update_core(
            session = session,
            project = project,
            workflow = workflow,
            name = input['name'],
            time_window = input.get('time_window', None),
            active = input['active'],
            mode = input['mode'],
            log = log,
            member = user.member)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        log['success'] = True
        return jsonify(
            workflow = workflow.serialize_with_actions(session = session),
            log = log), 200


def flow_update_core(
    session,
    project,
    workflow,
    name,
    active,
    time_window,
    mode,
    log,
    member):
    if mode == "ARCHIVE":
        workflow.archived = True
        workflow.active = False
        remove_job_scheduling(workflow_id = workflow.id)
        session.add(workflow)

        return log

    if mode == "UPDATE":
        session.add(workflow)

        workflow.is_new = False

        workflow.name = name
        workflow.active = active
        if not workflow.active:
            remove_job_scheduling(workflow_id = workflow.id)
        else:
            add_job_scheduling(workflow_id = workflow.id)
        workflow.time_window = time_window
        workflow.member_updated = member

        Workflow.update_string_id(
            session = session,
            workflow = workflow)

        log['info']['update'] = "Success"

        return log
