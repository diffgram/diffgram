# OPENCORE - ADD
# This line indicates that the code below is part of the OPENCORE project and is being added to the file.

from methods.regular.regular_api import *
# This line imports all functions and classes from the regular_api module in the methods.regular package.

from shared.database.task.task import Task
# This line imports the Task class from the task module in the shared.database.task package.

# Assumption this is a view?
@routes.route('/api/v1/task/<int:task_id>/next-task-with-issues', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_next_issue(task_id):
    """
        Returns the ID of the next task with an issue within the task template.
    :param task_id: The ID of the current task.
    :return: A JSON response containing the log and task_id of the next task with an issue.
    """
    spec_list = []
    # spec_list is initialized as an empty list, but it is not used in the function.

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    # The regular_input.master function is called with the request object and an empty spec_list.
    # It returns a log dictionary, an input dictionary, and an untrusted_input dictionary.
    # The log dictionary contains error messages or success information.
    # The input dictionary contains the input data from the request.
    # The untrusted_input dictionary contains the input data that has not been validated.
    if len(log["error"].keys()) >= 1:
        # If there are any error messages in the log dictionary, a 400 Bad Request response is returned.
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        # A new session is created with the sessionMaker.session_scope() context manager.
        task_id = task_next_issue_core(session = session,
                                       task_id = task_id)
        # The task_next_issue_core function is called with the session and task_id as arguments.
        # The task_id of the next task with an issue is returned.

        log['success'] = True
        # The success key in the log dictionary is set to True.

        return jsonify(log = log,
                       task_id = task_id), 200
        # A JSON response is returned containing the log dictionary and the task_id of the next task with an issue.


def task_next_issue_core(session, task_id):
    """
        Returns the ID of the next task with an issue within the task template.
    :param session: A database session object.
    :param task_id: The ID of the current task.
    :return: The ID of the next task with an issue.
    """
    next_task_id = Task.get_next_task_with_issues(session = session,
                                                  task_id = task_id)
    # The get_next_task_with_issues method of the Task class is called with the session and task_id as arguments.
    # It returns the ID of the next task with an issue.

    return next_task_id
    # The ID of the next task with an issue is returned.
