from shared.database.task.task import Task
from shared.database.task.task_user import TaskUser


def assign_reviewer_to_task(session: 'Session', task: Task):
    """
        Assigns a reviewer to the given task based on the reviewer
        who has less tasks assigned on that job.
    :param session:
    :param task:
    :return:
    """
    # Get job avaialable reviewers
    job_reviewers = task.job.get_reviewers(session = session)

    reviewer_count = {}
    for reviewer in job_reviewers:
        relations = TaskUser.list(
            user_id = reviewer.id
        )
        task_ids = [elm.task_id for elm in relations]
        task_ids = set(task_ids)
        reviewer_count[reviewer.id] = {
            'task_count': len(task_ids),
            'obj': reviewer
        }

    min = 99999999
    reviewer_to_assign = None
    for user_id, count_data in reviewer_count.items():
        if reviewer_count[user_id]['task_count'] < min:
            min = reviewer_count[user_id]['task_count']
