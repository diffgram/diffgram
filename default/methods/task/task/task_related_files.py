from methods.regular.regular_api import *
from shared.database.task.task import Task
from flask import jsonify, request, Blueprint
from typing import Dict, List, Optional

routes = Blueprint('routes', __name__)

@routes.route('/api/v1/task/<int:task_id>/files', methods=['POST'])
@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
def task_related_files(task_id: int) -> tuple[Dict[str, any], int]:
    """
    Returns the ID of the next task with an issue within the task template.
    :param task_id:
    :return:
    """
    log, input_data = regular_input.master(request=request, spec_list=[])
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        task_id = task_related_files_core(session=session, task_id=task_id)
        log['success'] = True
        return jsonify(log=log, task_id=task_id), 200


def task_related_files_core(session, task_id: int) -> Optional[int]:
    """
    Gets the related files for a given task and returns their serialized data.
    :param session: The database session.
    :param task_id: The ID of the task.
    :return: The serialized data of the related files or None if there are no related files.
    """
    related_files = Task.get_related_files(session=session, task_id=task_id)
    related_files_data = []
    if related_files:
        for file in related_files:
            related_files_data.append(file.serialize())
    return related_files_data[0] if related_files_data else None
