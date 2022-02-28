# OPENCORE - ADD
from shared.permissions.job_permissions import Job_permissions
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.input import Input
from shared.database.source_control.file import File
from shared.database.task.job.job_working_dir import JobWorkingDir

def rebuild_label_map(label_file_list):
    colour_map = {}
    for label_file in label_file_list:
        colour_map[label_file.id] = label_file.colour

    return colour_map


def task_template_label_attach(session,
                               task_template,
                               project_directory=None,
                               ):
    """
    Get label files from project and attach
    to job

    want full project_directory object for label_file_colour_map

    A key part of the rationale here is that a
    job may have labels that are distinct from the project.

    Main point of having this here is flexability that
    if we change the way we represent jobs, we don't have to change
    the "upfront" logic in terms of attach ids.
    ie decouple which ids are attached to a job to whatever muck we
    need to do at launch time / "run" time.

    """

    if task_template.label_mode == "closed_all_available":

        label_file_list_serialized = []

        # Provided
        label_file_list = task_template.label_dict.get('label_file_list')

        if label_file_list:
            file_list = File.get_by_id_list(session, label_file_list)

        else:
            # Temporary fall back for migration
            print("label file list did not exist, using fall back")
            file_list = WorkingDirFileLink.file_list(
                session=session,
                working_dir_id=project_directory.id,
                limit=25,
                type="label")

            # Store for future reference here
            task_template.label_dict['label_file_list'] = [file.id for file in file_list]

        # Work
        for file in file_list:
            file_serialized = file.serialize_with_label_and_colour(session=session)

            # Make sure time stamps are wrapped in str() to avoid nested json / dict issues

            label_file_list_serialized.append(file_serialized)

        # For debugging issue with serailization here.
        # print(label_file_list_serialized)

        task_template.label_dict['label_file_list_serialized'] = label_file_list_serialized

        # Now in context of users being able to choose labels,
        # We rebuild this on launching

        task_template.label_dict['label_file_colour_map'] = rebuild_label_map(file_list)

    return True


@Job_permissions.by_job_id(
    project_role_list=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
def job_launch_limits_with_permission_check(
        session,
        job,
        log,
        job_id):
    return task_template_launch_limits(
        session,
        job,
        log)


def task_template_launch_limits(session,
                                task_template,
                                log):
    """

    """

    # Different permissions depending on conditions ie share type
    # For now don't require billing to be enabled for non market jobs
    #  sending to Market clearly needs billing enabled
    # Future may want to still restrict jobs to paid accounts
    # For now in context of wanting trainer orgs to try it this seems reasonable
    # Potentially a lot to think about here...

    project = task_template.project

    if task_template.share_type == "Market":
        if project.api_billing_enabled is not True:
            log['error']['billing'] = "Please enable billing or select Project / Org for share type. "

    # TODO  Limit count of active jobs? ie default to 3 active jobs?
    # Limit on number of files? ie default to 500 files max per job?

    # Basic info
    # For now this is checked by new job creation
    # so low priorty to double check here
    if task_template.status not in ['draft']:
        log['error']['job_status'] = "Job already launched."

    # Files
    task_template.update_file_count_statistic(session=session)
    attached_dir_list = session.query(JobWorkingDir).filter(
        JobWorkingDir.job_id == task_template.id
    ).all()
    if task_template.file_count_statistic == 0 and len(attached_dir_list) == 0:
        log['error']['attached_dir_list'] = "Must attach at least 1 file or directory"

    if task_template.file_count:
        if task_template.file_count_statistic != task_template.file_count:
            log['error']['file_count'] = str(task_template.file_count_statistic) + " processed files " + \
                                         "does not match set file_count: " + str(task_template.file_count)

    # note we are querying the input table here
    # suspect this is better then getting all the files
    # and doing a query for each to input
    # ie for getting bulk file status?

    # For retrying we may want to not include "removed" files
    # But a challenge here is that we are querying input not other thing
    # Also not sure if this really handles "failed" ones well...

    result = Input.directory_not_equal_to_status(
        session=session,
        directory_id=task_template.directory_id)

    # TODO may be some cases that this is overbearing / needs to be handled better
    # ie could call directory_not_equal_to_status with return type
    # of "objects" or something...

    print(result)

    if result > 0:
        log['error']['file_status'] = f"Files processing. Try again in 30-60 minutes."

    # Credentials
    # ie Warn if missing ...
    # ie log['warn']['credentials'] = "No credentials required"

    # TODO if job type is exam check if grants at least one credential?

    # Guides

    if task_template.share_type in ["market"]:
        if task_template.guide_default_id is None:
            log['error']['guide_default'] = "Missing default guide"

    if task_template.type == "Normal":

        if task_template.guide_review_id is None:
            # Default review guide to being same as defualt guide
            # until we can handle this in better way
            task_template.guide_review = task_template.guide_default
            session.add(task_template)

        # Don't log error for now, see above default
        # log['error']['guide_review'] = "Missing review guide"

        # Bid(S)

    # Label check
    label_count = WorkingDirFileLink.file_list(session=session,
                                               working_dir_id=task_template.project.directory_default_id,
                                               type="label",
                                               counts_only=True, )
    if label_count == 0:
        log['error']['count'] = "Project must have at least 1 label"

    return log
