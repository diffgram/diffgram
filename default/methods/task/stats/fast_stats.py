from methods.regular.regular_api import *
from shared.database.task.job.job import Job
from shared.database.user import User
from shared.database.task.task import Task
from shared.database.annotation.instance import Instance

@routes.route('/api/job/<job_id>/stat', methods=["GET"])
def job_stat(job_id):
    with sessionMaker.session_scope() as session:
        job = Job.get_by_id(session, job_id).__dict__
        job.pop('_sa_instance_state', None)
        return jsonify({
            "total": job["stat_count_tasks"],
            "completed": job["stat_count_complete"]
            })

@routes.route('/api/job/<job_id>/user/<user_id>/stats', methods=["GET"])
def jon_user_stats(job_id, user_id):
    with sessionMaker.session_scope() as session:
        tasks = Task.list(
            session, 
            job_id=job_id,
        )
        instances_of_tasks = []
        task_list = []
        for task in tasks:
            task_dict = task.__dict__
            task_dict.pop('_sa_instance_state', None)
            task_dict.pop('job', None)
            task_dict.pop('incoming_directory', None)
            task_list.append(task_dict)

        return_task_list = [task for task in task_list if task["assignee_user_id"] == int(user_id)]
        completed = [task for task in return_task_list if task["status"] == "complete"]
        in_progress = [task for task in return_task_list if task["status"] == "in_progress"]
        deferred = [task for task in return_task_list if task["status"] == "deferred"]

        for task in return_task_list:
            file_id = task["file_id"]
            instances = Instance.list(
                session,
                file_id = file_id
            )
            for instance in instances:
                instance_dict = instance.__dict__
                instance_dict.pop('_sa_instance_state', None)
                instances_of_tasks.append(instance_dict)

        return jsonify({
            "total": len(return_task_list),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "deferred": len(deferred),
            "instaces_created": len(instances_of_tasks)
        })