import threading
import time
from sqlalchemy.orm import Session
from shared.database.project import Project
from shared.database.task.task import Task
from shared.database.task.job.job import Job
from shared.database.export import Export
from shared.database.source_control.working_dir import WorkingDir
from shared.regular import regular_log
from shared.helpers import sessionMaker
from shared.export.export_utils import check_export_billing, check_export_permissions_and_status
from flask import copy_current_request_context, jsonify
from shared.permissions.job_permissions import Job_permissions
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()

def create_new_export(session: Session,
                      project: Project,
                      source: str = None,
                      task_id: int = None,
                      job_id: int = None,
                      directory_id: int = None,
                      file_comparison_mode: str = None,
                      kind: str = None,
                      masks: str = None,
                      ann_is_complete: bool = False,
                      wait_for_export_generation: bool = False,
                      return_type: str = 'data',

                      log: dict = regular_log.default()):
    project_string_id = project.project_string_id

    @copy_current_request_context
    def export_on_thread(project_string_id, export_id):

        with sessionMaker.session_scope_threaded() as session:
            export_web_core(session = session,
                            project_string_id = project_string_id,
                            export_id = export_id)

        t.cancel()

    if source == "task":

        task = Task.get_by_id(
            session = session,
            task_id = task_id
        )
        if task is None:
            log["error"]["task_id"] = "Invalid task id"
            return False, log
        job = task.job

    elif source == "job":
        job = Job.get_by_id(session, job_id)

    # need directory for label stuff right
    directory = None

    if source in ["task", "job"]:
        Job_permissions.check_job_after_project_already_valid(
            job = job,
            project = project)

        directory = job.completion_directory
    # need directory for label stuff right
    if not directory:
        directory = WorkingDir.get_with_fallback(
            session = session,
            project = project,
            directory_id = directory_id)

    if directory is None:
        log["error"]["directory"] = "Invalid directory"
        return False, log

    # Caution assumes project.user_primary
    # Billing check
    log = check_export_billing(
        session = session,
        project = project,
        directory = directory,
        member = project.user_primary.member,
        log = log)

    if len(log["error"].keys()) >= 1:
        return False, log

    # TODO - the directory we pull from may need to make sense in terms of job or not...

    # Class Export() item to track it
    export = Export(
        project = project,
        file_comparison_mode = file_comparison_mode,
        kind = kind,
        source = source,
        masks = masks,
        job_id = job_id,
        task_id = task_id,
        ann_is_complete = ann_is_complete,
        working_dir_id = directory.id
    )

    if export.kind not in ["Annotations", "TF Records"]:
        log["error"]["kind"] = "Invalid kind"
        return False, log

    session.add(export)
    session.flush()

    # Long running operation
    if wait_for_export_generation is False:

        t = threading.Timer(0, export_on_thread, args = (
            project_string_id, export.id,))

        t.daemon = True
        t.start()
        result = {
            'success': True,
            'export': export.serialize()
        }
        return result, log

    # Immediate return, ie for mock test data
    else:
        export_web_core(
            session = session,
            project_string_id = project_string_id,
            export_id = export.id)

        export_check_result = check_export_permissions_and_status(
            export, project_string_id, session)

        if regular_log.log_has_error(export_check_result):
            return False, export_check_result

        result = export_view_core(
            export = export,
            format = "JSON",
            return_type = return_type)
        # If it's a TF records or other cases it will be ignored?

        return result, log

def export_web_core(session,
                    project_string_id,
                    export_id,
                    use_request_context = True
                    ):
    project = Project.get(session, project_string_id)

    time.sleep(.250)  # Give export time to hit database

    export = Export.get_by_id(session, export_id)

    if export is None:

        time.sleep(2)
        export = Export.get_by_id(session, export_id)

        if export is None:
            # TODO log a failure / update status better?
            print("Error no export found, export id is:", export_id)
            return False

    if not project:
        logger.error('Error: no project given.')
        return False

    if export.source in ["directory", "job", "task"]:
        # user = User.get(session)
        # TODO why not pass export object?
        result, data = Export.new_external_export(
            session = session,
            project = project,
            export_id = export_id,
            working_dir = export.working_dir,
            use_request_context = use_request_context
        )
