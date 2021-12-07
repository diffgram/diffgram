from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/modify', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_modify(project_string_id, task_id):
    with sessionMaker.session_scope() as session:
        spec_list = [
            {'user_id': {
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

        result, log = task_user_modify_core(session = session,
                                            task_id = task_id,
                                            project_string_id = project_string_id,
                                            user_id_list = input['user_id'],
                                            relation = input['relation'],
                                            log = log)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(task_user = result, log = log)


def task_user_modify_core(session, task_id, project_string_id, user_id_list, relation, log):
    result = {}
    users_to_remove = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(
        TaskUser.relation == relation)
    if (len(user_id_list) > 0):
        users_to_remove = users_to_remove.filter(TaskUser.user_id.notin_(user_id_list))

    for user_to_remove in users_to_remove.all():
        user_to_remove_id = user_to_remove.__dict__["id"]

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        result, log = task_user_remove_core(
            session = session,
            task_user_id = user_to_remove_id,
            project_string_id = project_string_id,
            log = log
        )

    for user in user_id_list:
        user_already_assigned = session.query(TaskUser).filter(TaskUser.user_id == user).filter(
            TaskUser.task_id == task_id).filter(TaskUser.relation == relation).all()
        if (len(user_already_assigned) > 0):
            continue

        result, log = api_task_user_add_core(
            session = session,
            task_id = task_id,
            user_id = user,
            relation = relation,
            project_string_id = project_string_id,
            log = log
        )
    return result, log


def api_task_user_add_core(session: 'Session',
                           task_id: int,
                           user_id: int,
                           relation: str,
                           project_string_id: str,
                           log: dict):
    task = Task.get_by_id(session, task_id)

    project = Project.get_by_string_id(session, project_string_id = project_string_id)

    if task.project_id != project.id:
        log['error']['project_id'] = 'Project and Task ID mismatch. Task does not belong to project.'
        return False, log

    user = User.get_by_id(session, user_id)
    if relation == 'reviewer':
        relation = task.add_reviewer(session = session, user = user)
        return relation.serialize(), log
    elif relation == 'assignee':
        relation = task.add_assignee(session = session, user = user)
        return relation.serialize(), log
    else:
        log['error']['relation'] = 'Invalid relation type. Only support "reviewer", "assignee"'
        return False, log


def task_user_remove_core(session: 'Session',
                          task_user_id: int,
                          project_string_id: str,
                          log: dict):
    project = Project.get_by_string_id(session, project_string_id = project_string_id)

    task_user = TaskUser.get_by_id(session = session, task_user_id = task_user_id)

    if task_user.task.project_id != project.id:
        log['error']['project_id'] = 'Project and TaskUser mismatch. TaskUser does not belong to project.'
        return False, log

    if task_user:
        session.delete(task_user)
        return True, log
    else:
        log['error']['task_user'] = 'Cannot find given task user relation'
        return False, log
