# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.task.job.job import Job
from flask import jsonify
from typing import Dict, List, Optional

@routes.route('/api/v1/job/<int:task_template_id>/members-list', methods=['GET'])
@Job_permissions.by_job_id(
    project_role_list=["admin", "Editor", "annotator"],
    apis_project_list=[],
    apis_user_list=["api_enabled_builder"])
def task_template_members_list_api(task_template_id: int) -> tuple[str, int]:
    """
    Get the list of members for a given task template.

    :param task_template_id: The ID of the task template.
    :return: A serialized list of members and a 200 HTTP status code.
    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        members_serialized, log = task_template_members_list_core(session, task_template_id, log)
        if members_serialized is False:
            return jsonify(log), 404
        return jsonify(members_serialized), 200


def task_template_members_list_core(session: sessions.Session, job_id: int, log: Dict[str, any]) -> tuple[Dict[str, List[Dict[str, str]]], Dict[str, any]]:
    """
    Get the list of members (reviewers and assignees) for a given task template.

    :param session: The database session.
    :param job_id: The ID of the task template.
    :param log: The logging dictionary.
    :return: A serialized list of members and the log dictionary.
    """
    task_template = Job.get_by_id(session, job_id)
    if task_template is None:
        log['error'] = "Task Template does not exist."
        return False, log

    reviewers = task_template.get_reviewers(session)
    assignees = task_template.get_assignees(session)

    reviewers_serialized = [user.serialize() for user in reviewers]
    assignees_serialized = [user.serialize() for user in assignees]

    return {
        "reviewers": reviewers_serialized,
        "assignees": assignees_serialized
    }, log
