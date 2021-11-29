from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/modify', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_modify(project_string_id, task_id):
    with sessionMaker.session_scope() as session:
        spec_list = [{'user_id': {
            'required': True,
            'kind': list
        }},
            {'relation': {
                'required': True,
                'kind': str,
                'valid_values_list': ['reviewer', 'assignee']
            }}
        ]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        
        for user in input['user_id']:
            user_already_assigned = TaskUser.get(session, user, task_id, input['relation'])
            if (user_already_assigned):
                task_user_id_to_remove = user_already_assigned.__dict__["id"]

                log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
                if len(log["error"].keys()) >= 1:
                    return jsonify(log = log), 400

                result, log = task_user_remove_core(
                    session = session,
                    task_user_id = task_user_id_to_remove,
                    project_string_id = project_string_id,
                    log = log
                )

                return jsonify(removed = result, log = log)
                
            result, log = api_task_user_add_core(
                session = session,
                task_id = task_id,
                user_id = user,
                relation = input['relation'],
                project_string_id = project_string_id,
                log = log
            )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(task_user = result, log = log)


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