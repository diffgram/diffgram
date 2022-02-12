# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.user import UserbaseProject

from shared.database.task.job.job import Job
from shared.database.task.task import Task

from methods.source_control import working_dir  # rename new to directory in the future
from shared.regular import regular_log


# Assumption this is a view?
@routes.route('/api/v1/task',
              methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
def task_by_id_api():
    """

    """
    spec_list = [{'task_id': int},
                 {'builder_or_trainer_mode': str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if regular_log.log_has_error(log): return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        task_serialized = task_by_id_core(session = session,
                                          task_id = input['task_id'],
                                          input = input)

        log['success'] = True
        return jsonify(log = log,
                       task = task_serialized), 200


@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_by_id_core(session,
                    task_id,
                    input):
    task = Task.get_by_id(session = session,
                          task_id = task_id)

    if input['builder_or_trainer_mode'] == "builder":
        task_serialized = task.serialize_builder_view_by_id(session)

    if input['builder_or_trainer_mode'] == "trainer":
        # TODO
        task_serialized = task.serialize_trainer_annotate(session)




    return task_serialized
