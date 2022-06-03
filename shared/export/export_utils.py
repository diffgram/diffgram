# OPENCORE - ADD
from shared.database.task.job.job import Job
from shared.database.project import Project
from shared.regular import regular_log
from shared.shared_logger import get_shared_logger
from shared.feature_flags.feature_checker import FeatureChecker
from shared.settings import settings
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.annotation.instance import Instance
from shared.database.event.event import Event
import datetime

logger = get_shared_logger()

def generate_file_name_from_export(export, session):
    """
        Returns a string with the final filename for an export.
    :param export:
    :return:
    """

    # TODO (low priority) switch to starting to array with "".join() it
    # it's a bit faster and more importantly easier to read / check.

    filename = f"_diffgram_annotations__source_{str(export.source)}_"
    
    if export.source == "task":
        filename += str(export.task.id)

    if export.source == "job":
        job = Job.get_by_id(
            session=session,
            job_id=export.job_id)
        if job:
            filename += str(job.name)

    if export.source == "directory":
        filename += str(export.working_dir.nickname)

    # Always add timestamps to avoid duplicate names.
    filename += f"_datetime_{datetime.datetime.utcnow().isoformat()}"
    filename = filename.replace(":", "-")

    return filename


def has_project_permissions_for_export(export, project_string_id, session):
    log = regular_log.default()
    project = Project.get(session, project_string_id)
    # Theory is that if a user has access to project
    # They have access to download from project
    if export.project_id != project.id:
        log['error']['project_permissions'] = 'Permission error, invalid project export match'

    return log


def is_export_completed(export):
    log = regular_log.default()
    # Context of exposing this in SDK, and
    # it failing if the export is not ready
    # note it's "complete" and not "success"
    if export.status != "complete":
        log['error']['export'] = "Export not ready yet."
        log['export'] = export.serialize()
        return log
    return log


def check_export_permissions_and_status(export, project_string_id, session):
    project_perms = has_project_permissions_for_export(export, project_string_id, session)
    if regular_log.log_has_error(project_perms):
        return project_perms

    export_completed_result = is_export_completed(export)
    if regular_log.log_has_error(export_completed_result):
        return export_completed_result

    return regular_log.default()



def check_export_billing(
    session,
    project,
    directory,
    member,
    log):
    """

    """

    logger.info('Checking Limits for Plan')
    if settings.ALLOW_STRIPE_BILLING is False:
        return log

    checker = FeatureChecker(
        session = session,
        user = member.user,
        project = project
    )

    max_allowed_instances = checker.get_limit_from_plan('MAX_INSTANCES_PER_EXPORT')
    if max_allowed_instances is None:
        return log

    # Careful if it's a large project,
    # And no other areas / no billing ID it can hang here ina funny way
    # Put limit of 200 as a temp measure for this.

    # Free case, could error or success
    file_list = WorkingDirFileLink.file_list(
        session = session,
        working_dir_id = directory.id,
        type = "image",
        exclude_removed = True,
        limit = 200
    )

    new_instance_count = 0

    for file in file_list:
        new_instance_count += Instance.list(
            session = session,
            file_id = file.id,
            exclude_removed = True,
            return_kind = "count")

    logger.info(f"Checking limits for export with {new_instance_count} instances")

    if max_allowed_instances:
        if new_instance_count > max_allowed_instances:
            message = 'Free Tier Limit Reached - Max Instances Allowed: {}. But Export  has {} instances'.format(
                max_allowed_instances,
                new_instance_count
            )
            log['error']['over_free_plan_limit'] = True
            log['error']['active_instances'] = new_instance_count
            log['error']['free_tier_limit'] = message

            Event.new(
                kind = "export_generation_free_account_over_limit",
                session = session,
                member = member,
                success = False,
                project_id = project.id
            )

            return log
    return log