# OPENCORE - ADD
from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from shared.utils import job_dir_sync_utils
from shared.database.task.job.user_to_job import User_To_Job
from shared.utils.task.task_update_manager import Task_Update

# See interior function for permissions
@routes.route('/api/v1/job/cancel',
              methods = ['POST'])
@limiter.limit("10 per day")
def job_cancel_api():
    """

    MODES
        cancel
        hide
        delete?
        pause?
        ...?

    Arguments

    Returns
        Success
            success message http response

        Failure
            error message http response

    """

    spec_list = [
        {"job_id": {
            'kind': int,
            'default': None
        }
        },
        {"job_list": {
            # List of job dicts where the id is available
            'kind': list,
            'default': None
        }
        },
        {"mode": {
            'kind': str,
            'required': True,
            'valid_values_list': ['archive', 'cancel', 'delete']
        }

        }]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        ### MAIN
        user = User.get(session)
        member = get_member(session = session)
        job_list = []
        if input['job_list']:
            job_list = input['job_list']
        elif input['job_id']:
            job_list = [{'id': input['job_id']}]

        for job_untrusted in job_list:
            result, log = job_cancel_core(
                session = session,
                user = user,
                log = log,
                mode = input['mode'],
                job_id = job_untrusted.get('id'),
                member = member)

            if result is False:
                return jsonify(log = log), 400

        log['success'] = True
        return jsonify(log = log), 200


@Job_permissions.by_job_id(
    project_role_list = ["admin"],
    apis_user_list = ['api_enabled_builder'])
def job_cancel_core(session,
                    user,
                    log,
                    mode,
                    job_id,
                    member):
    """

    QUESTIONs
        option to "hide" job as well?

        What about super admin option to actually delete
        (ie for database clean up...)

    Arguments
        session, db ojbect
        user, class User object
        job, class Job object
        log, diffgram regular log dict

    Returns

    """
    job = Job.get_by_id(session = session,
                        job_id = job_id)

    if user is None or job is None:
        log['error']['user_job'] = "No user or job"
        return False, log

    # JOB LIMITs
    result, log = job_cancel_limits(session,
                                    log,
                                    user,
                                    job,
                                    mode)

    member = get_member(session = session)
    if result is False:
        return result, log

    # TASK spcific limits
    # Difference that a job may have tasks that
    # Aren't cancelable
    status_list = None

    if mode in ["cancel"]:
        status_list = ["created", "available", "active"]

    if mode in ["delete"]:
        # Don't allow even a super admin to delete completed
        # from this method?
        # QUESTION
        # For that matter should a "completed" job even be allowed to be deleted?
        status_list = ["draft", "created", "available", "active"]

    # TODO disallow deleting jobs that have
    # any completed tasks / transactions

    if status_list:

        # Just a question, is there really any point of doing this
        # If the the job was cancelled?
        # like maybe for deleting but status I don't know
        task_list = job.task_list(session = session,
                                  status_list = status_list)

        for task in task_list:

            if mode == "cancel":
                session.add(task)
                task.status = "cancelled"

            if mode == "delete":
                session.delete(task)

    if mode == "archive":
        # We may want to rename "hidden" to archived?
        session.add(job)
        job.status = 'archived'
        job.hidden = True
        job.member_updated = user.member

        # Assume we want to remove sync dirs on archive, we might remove if that is not the case.
        job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(job = job, session = session, log = log)
        job_dir_sync_manager.remove_job_from_all_dirs()
        task_list = job.task_list(session = session,
                                  status_list = status_list)
        for task in task_list:
            task_update = Task_Update(
                session = session,
                task = task,
                member = member,
                status = "archived"
            )
            task_update.main()


    if mode == "cancel":
        session.add(job)
        job.status = "cancelled"
        job.member_updated = user.member

    if mode == "delete":
        """
        Question, is there a better way to do this with
            CASCADE / sql rules?
            It feels a bit funny to do it this way
            BUT also want to be careful since so much reuse!!!
            ie wouldn't want to delete a guide that was 
            attached to a job on cascade
        """

        # What about a job's directory,
        # TODO what about deleting associated credential links / other tables?

        user_to_job = User_To_Job.get_single_by_ids(
            session = session,
            user_id = user.id,
            job_id = job.id)

        task_list = job.task_list(
            session)

        for task in task_list:

            if task.file.type == "video":
                # Is this the right way to delete stuff here?
                video_frame_query = WorkingDirFileLink.image_file_list_from_video(
                    session = session,
                    video_parent_file_id = task.file.id,
                    return_mode = "query"
                )
                # Not working yet!
                video_frame_query.delete()

            session.delete(task)
            session.delete(task.file)

        # TODO still getting an integrity error
        # Must be some file that exists related to this job?
        # Or some other file that got updated incorrectly?
        job_dir_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(job = job, session = session, log = log)
        job_dir_sync_manager.remove_job_from_all_dirs(soft_delete = False)
        session.delete(job)
        session.delete(user_to_job)

    return True, log


def job_cancel_limits(session,
                      log,
                      user,
                      job,
                      mode):
    """
    QUESTION Does order matter here? Doesn't appear too yet
    """

    # TODO check list of valid modes

    if mode == "cancel":
        if job.status not in ['active']:
            log['error']['job'] = "Job is not active."
            return False, log

    # WIP
    if mode == "hide":
        if job.status not in ['draft']:
            log['error']['job'] = ""
            return False, log

    if mode == "delete":

        # Allow only super admin to delete

        if user.is_super_admin is not True:
            log['error']['job'] = "Invalid permission. Please contact your super admin."
            return False, log

    return True, log
