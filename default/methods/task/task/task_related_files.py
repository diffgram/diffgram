# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task


# Assumption this is a view?
@routes.route('/api/v1/task/<int:task_id>/files', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_related_files(task_id):
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
        task_id = task_related_files_core(session = session,
                                          task_id = task_id)

        log['success'] = True
        return jsonify(log = log,
                       task_id = task_id), 200


def task_related_files_core(session, task_id):
    related_files = Task.get_related_files(session = session,
                                           task_id = task_id)
    files_data = []
    for file in related_files:
        files_data.append(file.serialize())
    return file
