# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task, TASK_STATUSES
from shared.database.task.task_event import TaskEvent
from methods.task.task.task_update import Task_Update


@routes.route('/api/v1/task/<int:task_id>/review', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_review_api(task_id):
    """

    """
    spec_list = [{'comment': str},
                 {'action': {
                     'kind': str,
                     'valid_values_list': ['approve', 'request_change']
                 }}
                 ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        task_serialized = task_review_core(session = session,
                                           task_id = task_id,
                                           action = input['action'],
                                           member = member)

        if task_serialized is False:
            log['info']['task'] = "No Task Found"
            return jsonify(log = log), 200

        log['success'] = True
        return jsonify(log = log,
                       task = task_serialized), 200


def task_review_core(session: 'Session',
                     task_id: int,
                     action: str,
                     member: 'Member'):
    task = Task.get_by_id(task_id = task_id)

    task_update_manager = Task_Update(
        session = session,
        task = task,
        member = member
    )
    if action == 'approve':
        TaskEvent.generate_task_review_complete_event(session = session, task = task, member = member)
        task_update_manager.session = TASK_STATUSES['complete']
        task_update_manager.main()
    if action == 'request_change':
        task_update_manager.session = TASK_STATUSES['requires_changes']
        task_update_manager.main()

    return task.serialize_builder_view_by_id()
