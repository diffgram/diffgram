from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job
from shared.database.task.credential.credential import Credential


# Permissions on secondary function
@routes.route('/api/v1/exam/pass',
              methods = ['POST'])
@limiter.limit("1 per second, 50 per minute, 500 per day")
def exam_pass_api():
    """
    Context of say passing an exam

    Calls credential core

    Also notifies user

    Still probably want some "basic" level check for credentials .. like

    Should the check be on the job to user link?
    ie "has been awarded"

    # Is handling "passing"
    # Seperate from a direct hit to granting credentials?
    # (part of concept of say notifications etc.

    """

    spec_list = [{'job_id': int}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        # Want to get permissions via the root job?
        examination = Job.get_by_id(session = session,
                                      job_id = input['job_id'])
        if examination is None:
            log['error']['job_id'] = 'invalid'
            return jsonify(log = log), 400

        # QUESTION do we want to use root_id or parent_id here

        log = exam_pass_core(
            session = session,
            job_id = examination.parent_id,
            examination = examination,
            log = log)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        log['success'] = True
        return jsonify(log = log), 200


@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor"],
    apis_project_list = [],
    apis_user_list = ["api_enabled_builder"])
def exam_pass_core(session,
                   job_id,
                   examination,
                   log):
    # CAUTION job_id is root job for permissions (Exam template so to speak?)
    # exam_instance is "instance" of the exam? (which is a type of job)
    # exam_instance.exam is the Exam() class stuff attached to job

    """
    Limits
        Hasn't been done before?
        Allow duplicate instances of a credential?
            May be relevant for certain types of "awards"
    """

    # We get the user from the job, since
    # an exam only has one user?

    # But then how we check for permissions is going to be different
    # Why do we want to store the job thing on the "user link" if
    # only one user is doing the exam anway

    # Maybe delcare an assignee for the exam?
    # Since multiple people could have the user_to_job link ie if reviewing

    # Still want to use job syntax since we can have job.exam? sigh

    # not sure if we should be calling this "exam instance" or job...
    # or maybe it should be "job_instance"?

    if examination.exam.credentials_awarded is True:
        log['error']['user_to_job'] = 'Credentials already awarded'
        return log

    session.add(examination)

    credential_awards_new(session = session,
                          exam_instance = examination)

    # Add granted to credential link

    notify_user_passed_exam(exam_instance = examination)

    return log


def credential_awards_new(session,
                          exam_instance):
    """

    Get credentials awarded from job (assume it does all?)


    Create credential instances
        Attach to user?


    """

    # CAUTION the credential type list is on the
    # root/parent job not the exam_instance!!

    user = exam_instance.exam.user_taking_exam

    # Credential types to be awarded
    credential_type_to_job_list = Credential_Type_To_Job.get_by_job_id(
        session = session,
        job_id = exam_instance.parent_id,
        awards_only = True
    )

    for credential_type_to_job in credential_type_to_job_list:
        # CAUTION this is the link we are iterating on not
        # the actual credential type

        credential_instance_new(credential_type = credential_type_to_job.credential_type,
                                user = user,
                                session = session)

    exam_instance.exam.credentials_awarded = True


def credential_instance_new(credential_type,
                            user,
                            session):
    """

    "Issue" new credential instance

    """

    credential = Credential(
        credential_type = credential_type,
        user = user,
        status = "active"
    )
    session.add(credential)


def notify_user_passed_exam(exam_instance):
    user = exam_instance.exam.user_taking_exam

    subject = "Congrats! You passed " + exam_instance.name

    message = "View your new credentials"

    communicate_via_email.send(
        email = user.email,
        subject = subject,
        message = message)
