# OPENCORE - ADD
from shared.database.task.job.job import Job
from shared.database.source_control.working_dir import WorkingDir
from shared.database.project import Project
from shared.regular import regular_log
import datetime


def generate_file_name_from_export(export, session):
    """
        Returns a string with the final filename for an export.
    :param export:
    :return:
    """

    # TODO (low priority) switch to starting to array with "".join() it
    # it's a bit faster and more importantly easier to read / check.

    filename = '_diffgram_annotations__source_' + str(export.source) + '_'
    
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
    filename += "_datetime_" + datetime.datetime.utcnow().isoformat()

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
