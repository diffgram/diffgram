# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from shared.utils.task import task_file_observers

from shared.utils.sync_events_manager import SyncEventManager
from shared.database.task.task_event import TaskEvent
from shared.utils.task.task_update_manager import Task_Update
from shared.database.task.task import TASK_STATUSES
from shared.utils.task import task_assign_reviewer
import random


def trigger_task_complete_sync_event(session, task, job, log):
    sync_event_manager = SyncEventManager.create_sync_event_and_manager(
        session = session,
        dataset_source_id = None,
        dataset_destination = None,
        description = None,
        file = task.file,
        job = task.job,
        input = None,
        project = task.job.project,
        created_task = None,
        completed_task = task,
        new_file_copy = None,
        transfer_action = None,
        event_effect_type = '',
        event_trigger_type = 'task_completed',
        status = 'init',
        member_created = None
    )
    logger.debug('Created sync_event {}'.format(sync_event_manager.sync_event.id))
    if job.completion_directory and job.output_dir_action in ['copy', 'move']:
        job_observable = task_file_observers.JobObservable(session = session,
                                                           log = log,
                                                           job = job,
                                                           task = task,
                                                           sync_events_manager = sync_event_manager)
        job_observable.notify_all_observers(defer = True)

    Event.new_deferred(
        session = session,
        kind = 'task_completed',
        project_id = task.project_id,
        member_id = get_member(session).id if get_member(session) else None,
        task_id = task.id,
        wait_for_commit = True
    )
    job.job_complete_core(session)


def send_to_review_randomly(session, task, task_update_manager):
    """
        Generates a random number and sends task to review based on the Job review
        chances.
    :param task:
    :return:
    """
    # Review chance is a number betwen 0-1
    review_chance = task.job.review_chance
    rand_num = random.uniform(0, 1)

    if rand_num <= review_chance:
        # In review Mode no sync event (unless post_review=True)
        task_update_manager.status = TASK_STATUSES['review_requested']
        task_update_manager.main()
        task_assign_reviewer.auto_assign_reviewer_to_task(
            session = session,
            task = task
        )
        return False
    else:
        task_update_manager.status = TASK_STATUSES['complete']
        task_update_manager.main()
        return True

def task_complete(session,
                  task,
                  new_file,
                  project,
                  member,
                  post_review = False):
    """

    Also handles new_file here,
    so for example if the child tasks ditacte that we do a review afterwards,
    we don't flag the file as complete

    This solves the "complete" problem, since the file is not really complete till it's reviewed
    right?
    And presumably we are going to hide controls anyway if in a different status

    """

    # TODO prevent completion of already complete tasks?

    # Check child tasks
    # Should create the event listeners before changing status
    trigger_sync_event = True

    if task.status == 'complete':
        return True, new_file

    else:
        job = task.job
        task_update_manager = Task_Update(
            session = session,
            task = task,
            member = member
        )
        if job.allow_reviews:

            if post_review:
                task_update_manager.status = TASK_STATUSES['complete']
                task_update_manager.main()
            else:
                trigger_sync_event = send_to_review_randomly(
                    session = session,
                    task = task,
                    task_update_manager = task_update_manager
                )
        else:
            task_update_manager.status = 'complete'
            task_update_manager.main()

        # Careful, this is only relevant for normal
        # tasks, not exams?
        if task.job_type == 'Normal' and job.file_handling == "isolation":
            merge_task(session = session,
                       job = job,
                       task = task)

        # this stuff could be applicable to exams and normal maybe
        new_file = new_file.toggle_flag_shared(session)

        # Only assign this here
        # since we don't want files showing up in project
        # dir till complete or what?
        session.add(new_file)
        new_file.job_id = job.id

    task.time_completed = datetime.datetime.utcnow()

    job = task.job
    session.add(job)

    # QUESTION Cache from file here?

    if task.job_type == 'Normal':

        if job.share_type == "Market":

            if task.is_live == True:
                result = task_complete_transaction_normal(session = session,
                                                          task = task)

    if task.job_type == 'Exam':
        result = task_complete_exam(session = session,
                                    task = task)
    # QUESTION
    # Notify Observers of task completion
    log = regular_log.default()
    if trigger_sync_event:
        trigger_task_complete_sync_event(
            session = session,
            task = task,
            job = job,
            log = log
        )

    return True, new_file


def cost_per_task(cost_per_instance,
                  count_instances_changed):
    amount = cost_per_instance

    if count_instances_changed == 0:
        return amount

    amount += cost_per_instance * count_instances_changed

    return amount


def merge_task(session,
               job,
               task):
    """

    Merge completed task work back in to original directory

    """
    # Merge back to PROJECT directory

    directory_id = job.completion_directory_id
    if directory_id is None:
        directory_id = job.project.directory_default_id

    file_id = task.file_original_id

    link = WorkingDirFileLink.file_link(session = session,
                                        working_dir_id = directory_id,
                                        file_id = file_id)
    session.add(link)

    # TODO consider how this effects committed
    # Is it safe to just "update" it this way?
    # SHould this be a built in method of WorkingDirFileLink

    link.file_id = task.file_id


def task_complete_transaction_normal(session,
                                     task):
    task.count_instances_changed = task.file.count_instances_changed

    # TODO more reflection on handling None vs 0 for this case
    if task.count_instances_changed == None:
        task.count_instances_changed = 0

    # TODO Better handling if trainer doesn't have an account created
    # Should have one when enabling API so this is more for testing / edge cases?
    # This is related to a builder completing a task (That's on the market)

    return True


def task_complete_exam(session,
                       task):
    """
    If there is anything else we want to record for an exam task
    it could go here.
    """
    pass
