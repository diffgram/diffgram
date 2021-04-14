# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task


# Assumption this is a view?
@routes.route('/api/v1/task/<int:task_id>/next-task-with-issues', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_next_issue(task_id):
    """
        Returns the ID of the next task with an issue within the task template.
    :param task_id:
    :return:
    """
    spec_list = []

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        task_id = task_next_issue_core(session = session,
                                       task_id = task_id)

        log['success'] = True
        return jsonify(log = log,
                       task_id = task_id), 200


def task_next_issue_core(session, task_id):
    next_task_id = Task.get_next_task_with_issues(session = session,
                                                  task_id = task_id)

    return next_task_id
