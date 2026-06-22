from methods.regular.regular_api import *
from shared.database.external.external import ExternalMap
from shared.database.task.task_user import TaskUser
from typing import List, Dict, Any, Union
from flask_restplus import Namespace, Resource
from sqlalchemy.orm import Session
from shared.database.models.task import Task, User

api = Namespace('TaskUser', description='Operations related to task users')

task_user_ns = api.namespace('task_user', description='Task user related operations')


@task_user_ns.route('/<int:task_id>/user/add')
class TaskUserAdd(Resource):
    @api.expect({
        'user_id_list': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'required': True,
            'location': 'json'
        },
        'relation': {
            'type': 'string',
            'enum': ['reviewer', 'assignee'],
            'required': True,
            'location': 'json'
        }
    })
    @api.response(400, 'Bad Request')
    @api.response(200, 'Success')
    @task_user_ns.doc('add_task_user')
    @Project_permissions.user_has_project(Roles=["admin", "Editor"], apis_user_list=["api_enabled_builder"])
    def post(self, task_id: int) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Add users to a task as reviewers or assignees.
        """
        with sessionMaker.session_scope() as session:
            log, input_data = regular_input.master(request=request, spec_list=[
                {'user_id_list': {
                    'required': True,
                    'kind': list
                }},
                {'relation': {
                    'required': True,
                    'kind': str,
                    'valid_values_list': ['reviewer', 'assignee']
                }}
            ])

            if log['error']:
                return jsonify(log=log), 400

            result, log = api_task_user_add_core(
                session=session,
                task_id=task_id,
                user_id_list=input_data['user_id_list'],
                relation=input_data['relation']
            )

            if log['error']:
                return jsonify(log=log), 400

            return jsonify(task_user=result, log=log)


def api_task_user_add_core(session: Session,
                           task_id: int,
                           user_id_list: List[int],
                           relation: str,
                           log: Dict[str, Any]
                           ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    resulted_users = []

    task = Task.get_by_id(session, task_id)

    for user_id in user_id_list:
        user = User.get_by_id(session, user_id)

        if not user:
            log['error']['user_id'] = f'User with ID {user_id} not found.'
            return False, log

        if relation not in ['reviewer', 'assignee']:
            log['error']['relation'] = 'Invalid relation type. Only support "reviewer", "assignee"'
            return False, log

        existing_assignments = session.query(TaskUser).filter(TaskUser.task_id == task_id).filter(TaskUser.relation == relation).filter(TaskUser.user_id == user_id).count()

        if existing_assignments > 0:
            log['error']['duplicate'] = f'User with ID {user_id} is already assigned to the task with relation {relation}.'
            return False, log

        if relation == 'reviewer':
            resulted_users.append(task.add_reviewer(session=session, user=user).serialize())
        elif relation == 'assignee':
            resulted_users.append(task.add_assignee(session=session, user=user).serialize())

    return resulted_users, log
