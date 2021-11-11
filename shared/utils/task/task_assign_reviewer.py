from shared.database.task.task import Task, TASK_STATUSES
from shared.database.task.task_user import TaskUser
from shared.utils.task.task_update_manager import Task_Update


def auto_assign_reviewer_to_task(session: 'Session', task: Task):
    """
        Assigns a reviewer to the given task based on the reviewer
        who has less tasks assigned on that job.

        If the task already has a reviewer, we will not do anything.
        To add an additional reviewer manually, please use task.add_reviewer()

    :param session:
    :param task:
    :return: user object with representing the reviewer assigned to task.
    """
    # Get job available reviewers
    job_reviewers = task.job.get_reviewers(session = session)

    reviewer_count = {}
    for reviewer in job_reviewers:
        relations = TaskUser.list(
            session = session,
            user_id = reviewer.id,
            job_id = task.job_id,
            relation = 'reviewer'
        )
        task_ids = [elm.task_id for elm in relations]
        task_ids = set(task_ids)

        reviewer_count[reviewer.id] = {
            'task_count': len(task_ids),
            'obj': reviewer
        }

    # Find the user with less tasks assigned.
    min = 99999999
    reviewer_to_assign = None
    for user_id, count_data in reviewer_count.items():
        if reviewer_count[user_id]['task_count'] < min:
            min = reviewer_count[user_id]['task_count']
            reviewer_to_assign = reviewer_count[user_id]['obj']

    if reviewer_to_assign:
        task.add_reviewer(session = session, user = reviewer_to_assign)
        task_update_mngr = Task_Update(
            session = session,
            task = task,
            status = TASK_STATUSES['in_review']
        )
        task_update_mngr.main()

    return reviewer_to_assign
