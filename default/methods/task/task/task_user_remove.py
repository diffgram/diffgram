from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap


@routes.route('/api/v1/project/<string:project_string_id>/task/<int:task_id>/user/add', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_task_user_remove(project_string_id, task_id):
    with sessionMaker.session_scope() as session:
        spec_list = [{'user_id': {
            'required': True,
            'kind': int
        }},
            {'relation': {
                'required': True,
                'kind': str
            }}
        ]

        log, input, untrusted_input = regular_input.master(request = request,
                                                           spec_list = spec_list)
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        result, log = task_user_remove_core(
            session = session,
            task_id = task_id,
            project_string_id = project_string_id,
            log = log
        )


def task_user_remove_core(session: 'Session', task_id: int, project_string: str, log: dict):

    result = None

    return result, log
