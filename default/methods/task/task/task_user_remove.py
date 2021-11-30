from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser


@routes.route('/api/v1/project/<string:project_string_id>/task/user/remove/<int:task_user_id>', methods = ['DELETE'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_remove(project_string_id, task_user_id):
    with sessionMaker.session_scope() as session:
        spec_list = []

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        result, log = task_user_remove_core(
            session = session,
            task_user_id = task_user_id,
            project_string_id = project_string_id,
            log = log
        )

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(removed = result, log = log)


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
