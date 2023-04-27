from methods.regular.regular_api import *
from shared.database.task.job.job import Job
from shared.database.user import User
from shared.database.task.task import Task
from shared.database.annotation.instance import Instance

@routes.route('/api/job/<job_id>/stat', methods=["GET"])
@Job_permissions.by_job_id(project_role_list = ["admin", "Editor", "Viewer", "annotator"], apis_user_list = ['builder_or_trainer'])
def job_stat(job_id):
    with sessionMaker.session_scope() as session:
        job = Task.stats(
            session,
            job_id,
        )
        return jsonify(job)

@routes.route('/api/v1/project/<string:project_string_id>/stats-tasks', methods=["GET"])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "annotator"], apis_user_list = ['builder_or_trainer'])
def project_stats(project_string_id):
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id = project_string_id)
        user_id = request.args.get('user_id')
        job = Task.stats(
            session,
            project_id = project.id,
            user_id = user_id,
        )
        return jsonify(job)

@routes.route('/api/job/<job_id>/user/<user_id>/stats', methods=["GET"])
@Job_permissions.by_job_id(project_role_list = ["admin", "Editor", "Viewer", "annotator"], apis_user_list = ['builder_or_trainer'])
def job_user_stats(job_id, user_id):
    with sessionMaker.session_scope() as session:

        if user_id is None or user_id == 'null':
            log = regular_log.default()
            log['error']['user_id'] = f"Invalid, user_id is {user_id}"
            return jsonify(log = log), 400

        tasks = Task.stats(
            session,
            job_id,
            user_id
        )

        return jsonify(tasks)