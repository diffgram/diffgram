from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/add', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_add(project_string_id, task_id):
    with sessionMaker.session_scope() as session:
        spec_list = [{'user_id_list': {
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

        result, log = api_task_user_add_core(
            session = session,
            task_id = task_id,
            user_id_list = input['user_id_list'],
            relation = input['relation'],
            project_string_id = project_string_id,
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(task_user = result, log = log)


def api_task_user_add_core(session: 'Session',
                           task_id: int,
                           user_id_list: list,
                           relation: str,
                           project_string_id: str,
                           log: dict):
    resulted_users = []

    task = Task.get_by_id(session, task_id)

    project = Project.get_by_string_id(session, project_string_id = project_string_id)

    if task.project_id != project.id:
        log['error']['project_id'] = 'Project and Task ID mismatch. Task does not belong to project.'
        return False, log 

    if relation != "reviewer" and relation != "assignee":
        log['error']['relation'] = 'Invalid relation type. Only support "reviewer", "assignee"'
        return False, log

    for user_id in user_id_list:
        users_already_assigned = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(TaskUser.relation == relation).filter(TaskUser.user_id == user_id).count()
        if (users_already_assigned > 0):
            continue

        user = User.get_by_id(session, user_id)

        if relation == 'reviewer':
            resulted_users.append(task.add_reviewer(session = session, user = user).serialize())
        elif relation == 'assignee':
            resulted_users.append(task.add_assignee(session = session, user = user).serialize())

    return resulted_users, log

