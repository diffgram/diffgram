from methods.regular.regular_api import *
from shared.database.task.task import Task, TASK_STATUSES
from shared.utils.task import task_complete as shared_task_complete


@routes.route('/api/v1/task/<int:task_id>/complete', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def api_task_complete(task_id):
    """

    """
    spec_list = []

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session = session)

        task_serialized = task_complete_core(session = session,
                                             task_id = task_id,
                                             member = member)

        if task_serialized is False:
            log['info']['task'] = "No Task Found"
            return jsonify(log = log), 200

        log['success'] = True
        return jsonify(log = log,
                       task = task_serialized), 200


def task_complete_core(session,
                       task_id: int,
                       member: 'Member'):
    task = Task.get_by_id(session, task_id = task_id)

    shared_task_complete.task_complete(
        session = session,
        task = task,
        new_file = task.file,
        project = task.project,
        member = member,
        post_review = False
    )

    return task.serialize_builder_view_by_id(session)
