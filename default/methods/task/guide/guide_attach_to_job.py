# OPENCORE - ADD
# Import necessary modules and classes
from methods.regular.regular_api import *
from shared.database.project import Project
from shared.database.user import User
from shared.database.task.job.job import Job
from shared.database.task.guide import Guide

# Flask route for attaching a guide to a job
@routes.route('/api/v1/guide/attach/job', methods=['POST'])
@limiter.limit("50000 per day")
def guide_attach_to_job_api():
    """
    API to attach guide to a job
    - Basic value quality checking
    - Calls guide_to_job_core()
    - Enforces the concept of allowing only one guide attached to each thing
    """
    spec_list = [{"guide_id": int},
                 {"job_id": int},
                 {"kind": str},
                 {"update_or_remove": str}]

    # Validate and preprocess input using regular_input.master()
    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # Process the request within a database session
    with sessionMaker.session_scope() as session:

        job = Job.get_by_id(session, input['job_id'])
        guide = Guide.get_by_id(session, input['guide_id'])

        # Call guide_to_job_core() to construct the guide-to-job link
        result, log = guide_to_job_core(session=session,
                                        log=log,
                                        guide=guide,
                                        job=job,
                                        job_id=input['job_id'],
                                        kind=input['kind'],
                                        update_or_remove=input['update_or_remove']
                                        )
        if result is False:
            return jsonify(log=log), 400

        # Return a success message
        log['success'] = True
        return jsonify(log=log), 200


@Job_permissions.by_job_id(project_role_list=["admin", "Editor"],
                           apis_user_list=['api_enabled_builder', 'security_email_verified'])
def guide_to_job_core(session,
                      log,
                      guide,
                      job,
                      job_id,
                      kind,
                      update_or_remove
                      ):
    """
    Constructs guide to job link
    - Basic value checking

    Arguments:
        session (session): Database session object
        log (dict): A dictionary to store log messages
        guide (Guide): Guide object
        job (Job): Job object
        kind (str): String indicating the kind of guide attachment

    Returns:
        result (bool): A boolean indicating the success or failure of the operation
        log (dict): Updated log dictionary
        guide_type_to_job: The constructed guide-to-job link or None
    """

    # TODO permissions / auth checking

    # TODO would we rather just use the ids here?
    # not clear on value of passing whole object

    # Convert kind and update_or_remove to lowercase for consistency
    kind = kind.lower()
    if kind not in ["default", "review"]:
        log['error']['kind'] = "Invalid kind"
        return False, log

    update_or_remove = update_or_remove.lower()
    if update_or_remove not in ["update", "remove"]:
        log['error']['kind'] = "Invalid update_or_remove"
        return False, log

    # Check if job and guide objects are valid
    if job is None and isinstance(job, Job) is True:
        log['error']['kind'] = "Invalid job"
        return False, log

    if guide is None and isinstance(guide, Guide) is True:
        log['error']['kind'] = "Invalid guide"
        return False, log

    # Remove the existing guide-to-job link if update_or_remove is "remove"
    if update_or_remove == "remove":
        guide = None

    # Set the guide_default or guide_review attribute of the job object
    if kind == "default":
        job.guide_default = guide

    if kind == "review":
        job.guide_review = guide

    # Return a success message
    return True, log
