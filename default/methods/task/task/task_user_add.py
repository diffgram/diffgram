from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/add', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_add(project_string_id, task_id):
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

        result = {}

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        
        for user in input['user_id']:
            users_already_assigned = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(TaskUser.relation ==  input['relation']).filter(TaskUser.user_id == user).count()
            if (users_already_assigned > 0):
                continue

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

