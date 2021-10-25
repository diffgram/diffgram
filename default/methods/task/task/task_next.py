# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task


# Assumption this is a view?
@routes.route('/api/v1/job/<int:job_id>/next-task', methods=['POST'])
def task_next(job_id):
    """

    """
    spec_list = [{'task_id': {'type': int, 'required': False}},
                 {'project_string_id': str},
                 {'direction': str},
                 {'assign_to_user': bool}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        task_serialized = task_next_core(session=session,
                                         project_string_id=input['project_string_id'],
                                         job_id=job_id,
                                         task_id=input['task_id'],
                                         input=input)

        if task_serialized is False:
            log['info']['task'] = "No Task Found"
            return jsonify(log=log), 200

        log['success'] = True
        return jsonify(log=log,
                       task=task_serialized), 200


@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
def task_next_core(session,
                   job_id,
                   project_string_id,
                   task_id,
                   input):

    assign_to_user = input['assign_to_user']

    if assign_to_user is True:
        task = Task.get_task_from_job_id(
            session=session,
            job_id=job_id,
            user = User.get(session),
            direction=input['direction'],
            assign_to_user=assign_to_user)

    else:
        task = Task.navigate_tasks_relative_to_given_task(
            session=session,
            task_id=task_id,   
            direction=input['direction']
            )

    if not task:
        return False

    task_serialized = task.serialize_builder_view_by_id(session)

    return task_serialized
