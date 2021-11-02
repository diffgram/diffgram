from methods.regular.regular_api import *

from shared.database.task.job.job import Job
from shared.database.task.credential.credential_type import Credential_Type
from shared.database.task.credential.credential_type_to_job import Credential_Type_To_Job


@routes.route('/api/v1/credential/type/attach/job',
              methods = ['POST'])
@limiter.limit("20 per day")
def credential_type_attach_to_job_api():
    """

    API to attach credential to a job
    Basic value quality checking
    Then calls ct_to_job_core()

    Permissions checked at ct_to_job_core()


    """
    spec_list = [{"credential_type_list": list},
                 {"job_id": int},
                 {"kind": str},
                 {"add_or_remove": str}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        ### MAIN
        user = User.get(session)
        member = user.member

        kind = input['kind']
        add_or_remove = input['add_or_remove']

        # TODO handle credential_types list to individual credential_types
        credential_type_list = input['credential_type_list']

        for credential_type in credential_type_list:

            credential_type_id = credential_type.get('id', None)
            credential_type = Credential_Type.get_by_id(session, credential_type_id)

            result, log, ct_to_job = ct_to_job_core(session = session,
                                                    log = log,
                                                    credential_type = credential_type,
                                                    job_id = input['job_id'],
                                                    kind = kind,
                                                    add_or_remove = add_or_remove
                                                    )
            if result is False:
                return jsonify(log = log), 400

        ####

        log['success'] = True
        return jsonify(log = log), 200


@Job_permissions.by_job_id(
    project_role_list = ["admin", "Editor"],
    apis_project_list = [],
    apis_user_list = ["api_enabled_builder"])
def ct_to_job_core(session,
                   log,
                   credential_type,
                   job_id,
                   kind,
                   add_or_remove
                   ):
    """
    Constructs credential to job link
    Basic value checking

    Arguments
        session, db session
        log, regular log dict
        credential_type, class Credential_Type object
        job, class Job object
        kind, string

    Returns
        result, bool
        log, updated log
        ONE OF
            credential_type_to_job object
            None

    """

    # TODO permissions / auth checking

    # TODO handle if this is "attaching" or "removing" similar operation

    # TODO would we rather just use the ids here?
    # not clear on value of passing whole object

    job = Job.get_by_id(session, job_id)

    kind = kind.lower()
    if kind not in ["requires", "awards", "remove"]:
        log['error']['kind'] = "Invalid kind"
        return False, log, None

    add_or_remove = add_or_remove.lower()
    if add_or_remove not in ["add", "remove"]:
        log['error']['kind'] = "Invalid add_or_remove"
        return False, log, None

    if job is None and isinstance(job, Job) is True:
        log['error']['kind'] = "Invalid job"
        return False, log, None

    if credential_type is None and isinstance(credential_type, Credential_Type) is True:
        log['error']['kind'] = "Invalid credential_type"
        return False, log, None

    # check existing
    existing = Credential_Type_To_Job.get_by_credential_and_job_ids(session = session,
                                                                    credential_type_id = credential_type.id,
                                                                    job_id = job.id)

    if add_or_remove == "add":
        # Only allow one, ie can't both require and awards?
        # What about changing
        if existing:
            log['error']['credential_type'] = "Existing credential attachement"
            return False, log, None

        credential_type_to_job = Credential_Type_To_Job()
        session.add(credential_type_to_job)

        credential_type_to_job.credential_type = credential_type
        credential_type_to_job.job = job
        credential_type_to_job.kind = kind

        return True, log, credential_type_to_job

    if add_or_remove == "remove":

        if not existing:
            log['error']['credential_type'] = "No existing credential"
            return False, log, None

        session.delete(existing)

    return True, log, None
