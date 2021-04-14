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
                 {'direction': str}]

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

        log['success'] = True
        return jsonify(log=log,
                       task=task_serialized), 200


@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
def task_next_core(session,
                   job_id,
                   project_string_id,
                   task_id,
                   input):
    task = Task.get_next_previous_task_by_task_id(session=session,
                                                  task_id=task_id,
                                                  job_id=job_id,
                                                  direction=input['direction'])

    if not task:
        return False

    task_serialized = task.serialize_trainer_annotate(session)

    return task_serialized
