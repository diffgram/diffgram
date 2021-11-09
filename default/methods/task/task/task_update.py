# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task
from shared.utils.task.task_update_manager import Task_Update


@routes.route('/api/v1/task/update',
              methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
def task_update_api():
    """

    """
    spec_list = [
        {'task_id': {
            'kind': int,
            'permission': 'task'
        }
        },
        {'task_ids': {
            'kind': list,
            'permission': 'task',
            'required': False
        }
        },
        {'mode': {
            'kind': str,
            'valid_values_list': ['toggle_deferred']
        }
        },
        {'status': {
            'kind': str,
            'valid_values_list': ['archived']
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        task_list = []
        
        member = get_member(session = session)

        if input['task_id']:
            task = Task.get_by_id(session = session,
                                  task_id = input['task_id'])
            task_list.append(task)
        else:
            task_list = Task.list(
                session = session,
                task_ids = input['task_ids']
            )
        for task in task_list:
            Permission_Task.by_task_id_core(task.id)
            task_update = Task_Update(
                session = session,
                task = task,
                mode = input['mode'],
                member = member,
                status = input['status']
            )

            task_update.main()

        if len(task_update.log["error"].keys()) >= 1:
            return jsonify(log = task_update.log), 400

        return jsonify(log = task_update.log), 200
