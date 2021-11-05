from methods.regular.regular_api import *
from methods.task.task.task_update import Task_Update

@routes.route('/api/v1/project/<string:project_string_id>' +
              '/task/next',
              methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 1000 per day")
@Project_permissions.user_has_project(
    ["admin", "Editor", "Annotator"])
def api_get_next_task_annotator(project_string_id):

    log = regular_input.regular_log.default_api_log()

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)
        user = User.get(session)
        
        if not user:
            log['error']['usage'] = "Designed for human users."
            return jsonify( log = log), 200

        task = get_next_task_by_project(
            session = session,
            user = user,
            project = project)

        if task is None:
            log['info']['task'] = "No tasks available."
            return jsonify( log = log), 200

        task_serialized = task.serialize_trainer_annotate(session)

        log['success'] = True
        return jsonify( log = log,
                        task = task_serialized), 200


def get_next_task_by_project(
        session,
        user,
        project):

    task = Task.get_last_task(
        session = session,
        user = user,
        status_allow_list = ["available", "in_progress"])

    if task:
        return task

    task = Task.request_next_task_by_project(
        session = session,
        project = project,
        user = user)

    if task:
        task.add_assignee(session, user)
        task_update_manager = Task_Update(
            session = session,
            task = task,
            status = 'in_progress'
        )
        task_update_manager.main()  # This updates the task status
        session.add(task)
        session.add(user)


    return task


def get_next_task_by_job(
        session,
        user,
        job):

    task = Task.get_last_task(
        session = session,
        user = user,
        status_allow_list = ["available", "in_progress"])

    if task:
        return task

    task = recursively_get_next_available(session = session,
                                          job = job,
                                          user = user)

    if task:
        task.add_assignee(session, user)
        task_update_manager = Task_Update(
            session = session,
            task = task,
            status = 'in_progress'
        )
        # set status
        task_update_manager.main()  # This updates the task status
        session.add(task)
        session.add(user)

    return task


@routes.route('/api/v1/job/<int:job_id>/task/next',
              methods = ['POST'])
@limiter.limit("1 per second, 1000 per day")
@Job_permissions.by_job_id(	
    mode = "builder",
    apis_user_list = ['builder_or_trainer', 'security_email_verified'])
def task_next_by_job_api(job_id):

    log = regular_input.regular_log.default_api_log()

    with sessionMaker.session_scope() as session:

        job = Job.get_by_id(session, job_id)
        user = User.get(session)

        task = get_next_task_by_job(
            session = session,
            user = user,
            job = job)

        if task is None:
            log['info']['task'] = "No tasks available."
            return jsonify( log = log), 200

        task_serialized = task.serialize_trainer_annotate(session)

        log['success'] = True
        return jsonify( log = log,
                        task = task_serialized), 200




def recursively_get_next_available(session,
                                   job,
                                   user):
    """
    Goal, give consideration to task types,
    and not expect that first result from shared.database
    matches "business?" logic

    Example of saying a person can't review their own task

    """

    ignore_task_IDS_list = []

    while True:

        task = Task.get_next_available_task_by_job_id( 
            session = session,
            job_id = job.id,
            ignore_task_IDS_list = ignore_task_IDS_list)

        if task is None:
            return None

        if task.task_type == 'draw':
            return task

        if task.task_type == 'review':

            result = valid_review_task_for_user(session = session,
                                                task = task,
                                                user = user)

            if result is True:
                return task

            else:
                ignore_task_IDS_list.append(task.id)


def valid_review_task_for_user(session,
                               task,
                               user):

    parent = Task.get_by_id(session, task.parent_id)
    # task.parent not working for some reason

    if parent:
        if user == parent.assignee_user:
            return False
    
    return True