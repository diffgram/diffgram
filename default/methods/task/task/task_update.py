# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.task import Task
from shared.database.permission_task.permission_task import Permission_Task
from shared.utils.task.task_update_manager import Task_Update
from typing import Dict, List, Union

@routes.route('/api/v1/task/update',
              methods=['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
def task_update_api() -> Dict[str, Union[str, int]]:
    """
    Update tasks in various ways.
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
            'valid_values_list': ['toggle_deferred', 'incomplete']
        }
         },
        {'status': {
            'kind': str,
            'valid_values_list': ['archived']
        }
         }
    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        task_list = []

        member = get_member(session=session)

        if 'task_id' in input and input['task_id'] is not None:
            task = Task.get_by_id(session=session,
                                  task_id=input['task_id'])
            if task is None:
                return jsonify(log={'error': 'Task not found'}), 404
            task_list.append(task)
        elif 'task_ids' in input and input['task_ids'] is not None:
            if len(input['task_ids']) == 0:
                return jsonify(log={'error': 'No tasks provided'}), 400
            task_list = Task.list(session=session,
                                  task_ids=input['task_ids'][:100])
            if len(task_list) == 0:
                return jsonify(log={'error': 'No tasks found'}), 404
        else:
            return jsonify(log={'error': 'No tasks provided'}), 400

        for task in task_list:
            Permission_Task.by_task_id_core(task.id)
            if 'mode' not in input or input['mode'] is None:
                return jsonify(log={'error': 'Mode is required'}), 400
            if 'status' not in input or input['status'] is None:
                return jsonify(log={'error': 'Status is required'}), 400

            task_update = Task_Update(
                session=session,
                task=task,
                mode=input['mode'],
                member=member,
                status=input['status']
            )

            task_update.main()

            if len(task_update.log["error"].keys()) >= 1:
                return jsonify(log=task_update.log), 400

        return jsonify(log=task_update.log), 200
