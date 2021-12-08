from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/remove', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_remove(project_string_id, task_id):
    with sessionMaker.session_scope() as session:
        spec_list = [
            {'user_id_list': {
            'required': False,
            }},
            {'relation': {
                'required': True,
                'kind': str,
                'valid_values_list': ['reviewer', 'assignee']
            }},
        ]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        result, log = task_user_remove_core(
            session = session,
            task_id = task_id,
            user_id_list = input['user_id_list'],
            relation = input['relation'],
            project_string_id = project_string_id,
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(removed = result, log = log)


def task_user_remove_core(session: 'Session',
                          task_id: int,
                          user_id_list: int,
                          relation: str,
                          project_string_id: str,
                          log: dict):
    project = Project.get_by_string_id(session, project_string_id = project_string_id)
    task = Task.get_by_id(session, task_id)

    if task.project_id != project.id:
        log['error']['project_id'] = 'Project and Task ID mismatch. Task does not belong to project.'
        return False, log

    if relation != "reviewer" and relation != "assignee":
        log['error']['relation'] = 'Invalid relation type. Only support "reviewer", "assignee"'
        return False, log

    for user_id in user_id_list:
        users_already_assigned = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(TaskUser.relation == relation).filter(TaskUser.user_id == user_id).count()
        if (users_already_assigned < 1):
            continue

        task_user = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(TaskUser.relation == relation).filter(TaskUser.user_id == user_id)

        if task_user:
            task_user.delete()

    return True, log
