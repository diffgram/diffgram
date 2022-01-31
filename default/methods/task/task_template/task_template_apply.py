from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from shared.database.task.job.user_to_job import User_To_Job
from shared.database.task.credential.credential import Credential
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job
from shared.database.task.exam.exam import Exam

from shared.utils.task import task_new


@routes.route('/api/v1/task-template/apply',
              methods = ['POST'])
@General_permissions.grant_permission_for(
    Roles = ['normal_user'],
    apis_user_list = ["builder_or_trainer"])
@limiter.limit("20 per day")
def task_template_apply_api():
    """

    Checks if user is authorized to start work on a project
    If so, grants access to a user

    * Basic input checking from untrusted source
    * Checks all job limits (user, job, credential...)

    QUESTION
        How would we want to do this if say an
        admin user / org manager wanted to add people to a job...

    ASSUMPTIONS
        - Assumes user is the user making the request...
        - We will want different method from removing a user from a job
            ie that it requires less checks to remove a user, isn't a simple add/delete


    Arguments

    Returns
        Success
            actions to add user to job
            success message http response

        Failure
            error message http response

    """

    spec_list = [{"task_template_id": int}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        ### MAIN
        user = User.get(session)
        task_template = Job.get_by_id(session, input['task_template_id'])

        result, log = task_template_apply_core(session,
                                               user,
                                               task_template,
                                               log)

        if result is False:
            return jsonify(log = log), 400

        log['success'] = True
        return jsonify(log = log), 200


def task_template_apply_core(session,
                             user,
                             task_template,
                             log,
                             do_check_limits: bool = True):
    """
    Arguments
        session, db ojbect
        user, class User object
        job, class Job object
        log, diffgram regular log dict

    Returns

    """
    if user is None or task_template is None:
        log['error']['user_job'] = "No user or job"
        return False, log

    if do_check_limits is True:
        result, log = all_limits(session,
                                 log,
                                 user,
                                 task_template)

        if result is False:
            return result, log

    if task_template.type == "exam_template":
        new_job = task_template_apply_exam(session = session,
                                           user = user,
                                           og_task_template = task_template)
    else:
        log['error']['task_template_type'] = 'Can only apply to Task templates with type exam_template'
        return False, log

    # Serialize whole thing or???
    log['job_id'] = new_job.id
    # Job id is now Exam job, we return it so we can send
    # user to new Exam

    return True, log


# TODO move to exam folder?

def task_template_apply_exam(session,
                             user,
                             og_task_template):
    # QUESTION not sure if it makes sense to have this logic here,
    # Maybe should be in a job_exam area or something

    # Need to create new job first
    task_template = copy_task_template_for_exam(session = session,
                                                og_task_template = og_task_template,
                                                user = user)

    # then attach the user to that new job (not the "root" one?)
    user_to_job = task_template.attach_user_to_job(
        session = session,
        user = user,
        add_to_session = True
    )

    # Attach assignees as reviewers for tasks
    parent_assignees = og_task_template.get_assignees(session)

    result = task_new.provision_root_tasks(session = session,
                                           job = task_template,
                                           default_assignee = user,
                                           default_reviewers = parent_assignees)

    exam = Exam(user_taking_exam = user)
    session.add(exam)
    task_template.exam = exam

    return task_template


def copy_task_template_for_exam(session,
                                og_task_template,
                                user):
    """
    og == original

    Passing things like hidden to reduce:
    https://en.wikipedia.org/wiki/Confused_deputy_problem

    TODO better way to "inherit" some of this stuff for exam?

    QUESTION should we pass the directory to the new job
    OR inherit it from parent? Doesn't seem to be a downside to passing the directory

    Passes per file? anything else?

    """
    # TODO how do we want to name exam jobs to avoid confusion
    name = og_task_template.name + " " + user.email

    # Override for now, so review freqeuncy is 1:1
    review_by_human_freqeuncy = "every_pass"

    # Clarify that the directory assigned here isn't for storage,
    # it's the original directory where the original files are stored
    # And we are not attaching files created in the *process* of a job to a directory yet

    # When we create a new job that's a template
    # We set is_template to True
    # Since this is copy for an exam, we do not want to copy
    # is_template (this is an instance)

    task_template_copy = Job(hidden = og_task_template.hidden,
                             security_require_email_verified = og_task_template.security_require_email_verified,
                             status = og_task_template.status,
                             type = 'examination',
                             # We want to differentiate between the exam template and the child exam
                             instance_type = og_task_template.instance_type,
                             permission = og_task_template.permission,
                             share_type = og_task_template.share_type,
                             project = og_task_template.project,
                             category = og_task_template.category,
                             guide_default = og_task_template.guide_default,
                             review_by_human_freqeuncy = review_by_human_freqeuncy,
                             allow_reviews = True,
                             directory = og_task_template.directory,
                             label_mode = og_task_template.label_mode,
                             label_dict = og_task_template.label_dict,
                             completion_directory_id = og_task_template.completion_directory_id,
                             name = name
                             )
    session.add(task_template_copy)
    session.flush()

    task_template_copy.parent_id = og_task_template.id

    # We don't stricly need a directory? since stuff is stored
    # In relationship to task graph?

    return task_template_copy


def all_limits(session,
               log,
               user,
               task_template):
    """
    QUESTION Does order matter here? Doesn't appear too yet
    """

    result, log = task_template_limits(session,
                                       log,
                                       user,
                                       task_template)

    if result is False:
        return result, log

    result, log = user_limits(session,
                              log,
                              user,
                              task_template)
    if result is False:
        return result, log

    result, log = credential_limits(session,
                                    log,
                                    user,
                                    task_template)
    if result is False:
        return result, log

    return True, log


def task_template_limits(session,
                         log,
                         user,
                         task_template):
    """
    All job related limits

    Returns
        Success
            True, log

        Failure
            False, log
    """

    # Job permisions / hidden?
    # Determine share type....

    # Job status is eligible to start?
    if task_template.hidden is True:
        log['error']['job'] = "Job does not exist."
        return False, log

    # TODO handle invite only and only me cases?
    if task_template.permission not in ['all_secure_users']:
        log['error']['permission'] = "Denied."
        return False, log

    if task_template.status not in ['active']:
        log['error']['status'] = "Denied. (Job status)"
        return False, log
    # Check job has available tasks? (or is that handled by status)

    # Does job require email to be verified? (Default is True)
    if task_template.security_require_email_verified is True:
        if user.security_email_verified is not True:
            log['error']['user_email_verified'] = "Please verify email"
            return False, log

    # Check if Examination for users already exists.
    examination_exists = task_template.examination_exists(session, user)
    if examination_exists:
        log['error']['examination_exists'] = "You've already applied to this exam."
        return False, log

    return True, log


def credential_limits(session,
                      log,
                      user,
                      task_template):
    """

    Check if user has credentials needed to start the job

    Returns
        Success
            True, log

        Failure
            False, log

    """
    # CAUTION, we don't require a job to have a credential
    # So if a job has no credentials, a user with no credentials
    # Could still start it (ie new users)

    # Get job credentials
    job_credential_type_list = Credential_Type_To_Job.get_by_job_id(
        session = session,
        job_id = task_template.id,
        requires_only = True,
        ids_only = True)

    if job_credential_type_list:

        assert type(job_credential_type_list[0]) is int

        # Get user credentials
        user_credential_list = Credential.get_by_user_id(session = session,
                                                         user_id = user.id,
                                                         status_is_valid = True)
        if user_credential_list is None:
            log['error']['user_credentials'] = "User has no credentials"
            return False, log

        # A user may have many more credentials than a job requires
        # BUT a user must have all the credentials that a job requires
        # slight challenge
        # Is that we are compaing credential.type not the credential directly

        user_credential_type_id_list = []
        for credential in user_credential_list:
            user_credential_type_id_list.append(credential.credential_type_id)

        missing = set(job_credential_type_list).difference(user_credential_type_id_list)

        # TODO list specific credentials....
        if missing:
            log['error']['user_credentials'] = "Missing required credentials"
            return False, log

    return True, log


def user_limits(session,
                log,
                user,
                task_template):
    """
    ie user hasn't started job previously etc...

    Returns
        Success
            True, log

        Failure
            False, log

    """

    # Has trainer API enabled

    if task_template.share_type == "Market":
        if user.api_enabled_trainer is not True:
            log['error']['api_enabled_trainer'] = "Please signup to be a Trainer."
            return False, log

    # User does not have too many jobs open..
    # Job and status in [...]
    # TODO Get user job count
    user_job_count = User_To_Job.get_all_by_user_id(session = session,
                                                    user_id = user.id,
                                                    status_is_active = True,
                                                    count_only = True)

    # if user_job_count is None, assumption is that userhas no jobs
    print(user_job_count)

    job_count_max = 999999

    if task_template.share_type == "market":
        if task_template.type == "Normal":
            job_count_max = 200

    if task_template.share_type in ["org", "project"]:
        job_count_max = 99999

    if user_job_count:
        # QUESTION would different users have differnt job maxes? probably
        if user_job_count >= job_count_max:
            log['error']['job_count_limit'] = "Too many jobs already"
            return False, log

    # Is not banned from job
    # QUESTION Where are we storing this?
    # ie a This is more of a user to org / user to user thing
    # may not be just for a specific job

    return True, log
