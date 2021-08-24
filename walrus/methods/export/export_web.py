# OPENCORE - ADD
from methods.regular.regular_api import *
from flask import copy_current_request_context
import threading
from shared.data_tools_core import Data_tools
from shared.database.export import Export
from methods.export.export_view import export_view_core
from shared.database.task.job.job import Job

data_tools = Data_tools().data_tools


# TODO merge this with "new" confusing to be in seperate files
@routes.route('/api/walrus/project/<string:project_string_id>' +
              '/export/to_file',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ["api_enabled_builder"])
@limiter.limit("10 per minute, 50 per day")
def web_export_to_file(project_string_id):
    """
    Generates annotations
    Assumes latest version if none provided...

    # TODO working on how we want to handle this especially in relationship to
    different branches and versions and working dirs...

    Shouldn't actually do latest should do the first version

    Long running operation (starts new thread)

    Input example (JSON)
    {
        directory_id: 1059
        file_comparison_mode: "latest"
        kind: "Annotations"
        masks: false
        source: "directory"
        version_id: 0
    }

    wait_for_export_generation == True
    is in conjunction with return_type

    For job permissions:
        We assume that we already are operating in context
        of project permissions, so as long as the job
        is in the project then it's fine.
        including things like API enabled builder

    """

    spec_list = [
        {"kind": str},  # ["Annotations", "TF Records"]
        {"source": str},  # ["job", "directory", "task", "version"]
        {"file_comparison_mode": str},
        {"masks": bool},

        # TODO could we merge all of these ids into
        # and "id" field, and then rely on the source thing? feels
        # strange to have it seperate like that...
        # would make it a lot cleaner...
        # ie "id" and may be of ["job", "directory", "version"]

        {"version_id": None},  # int, but not required?
        {"directory_id": None},  # int, but not required?
        {"job_id": None},
        {"task_id": None},
        {"return_type": None},  # ["url", "data"]
        {"wait_for_export_generation": {
            'default': False,
            'kind': bool
        }
        },
        {"ann_is_complete": {  # April 22, 2020, assumes "file" (not task)
            'default': None,  # None means all
            'kind': bool
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    @copy_current_request_context
    def export_on_thread(project_string_id, export_id):

        with sessionMaker.session_scope_threaded() as session:
            export_web_core(session = session,
                            project_string_id = project_string_id,
                            export_id = export_id)

        t.cancel()

    """
    Permission model for task
        if task exists, we set job from task
        then use same permissinon system as job.

        Did some manual tests account
        and worked as expected (denied for ids not in project)

        still feels a little bit brittle / a lot of little assumptions
        about stuff matching (ie source being checked / matching for 'task')
        string. but otherwise seems to work ok.

    """

    # TODO: if reusing the code somewhere else. Make sure to take it out into a separate function to
    # follow DRY.
    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        if input["source"] == "task":

            task = Task.get_by_id(
                session = session,
                task_id = input["task_id"]
            )
            if task is None:
                log["error"]["task_id"] = "Invalid task id"
                return jsonify(log = log), 400

            job = task.job

        elif input["source"] == "job":

            job = Job.get_by_id(session, input["job_id"])

        # need directory for label stuff right
        directory = None

        if input["source"] in ["task", "job"]:
            Job_permissions.check_job_after_project_already_valid(
                job = job,
                project = project)

            # TODO verify this is working as expected.
            directory = job.completion_directory
        # print("directory", directory)

        if not directory:
            directory = WorkingDir.get_with_fallback(
                session = session,
                project = project,
                directory_id = input["directory_id"])

        if directory is None:
            log["error"]["directory"] = "Invalid directory"
            return jsonify(log = log), 400

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        # TODO - the directory we pull from may need to make sense in terms of job or not...

        # Class Export() item to track it
        export = Export(
            project = project,
            file_comparison_mode = input['file_comparison_mode'],
            kind = input["kind"],
            source = input["source"],
            masks = input["masks"],
            job_id = input["job_id"],
            task_id = input["task_id"],
            ann_is_complete = input['ann_is_complete'],
            working_dir_id = directory.id
        )

        if export.kind not in ["Annotations", "TF Records"]:
            log["error"]["kind"] = "Invalid kind"
            return jsonify(log = log), 400

        session.add(export)
        session.flush()

        # Long running operation
        if input['wait_for_export_generation'] is False:

            t = threading.Timer(0, export_on_thread, args = (
                project_string_id, export.id,))

            t.daemon = True
            t.start()

            return jsonify(success = True,
                           export = export.serialize())

        # Immediate return, ie for mock test data
        else:
            export_web_core(
                session = session,
                project_string_id = project_string_id,
                export_id = export.id)

            result = export_view_core(
                export = export,
                format = "JSON",
                return_type = input['return_type'])
            # If it's a TF records or other cases it will be ignored?

            return jsonify(result), 200


def export_web_core(session,
                    project_string_id,
                    export_id,
                    use_request_context = True
                    ):
    project = Project.get(session, project_string_id)

    # TODO error handling
    # TODO review semantic segmentation mask in this context
    # semantic_segmentation_data_prep.generate_mask_core(s, project)

    # TODO why not store project with export?

    time.sleep(.250)  # Give export time to hit database
    # This is a hacky way to do it...

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

    if export.source == "version":

        # TODO use version id from export
        if id:
            version = session.query(Version).filter(Version.id == id).first()

        if not id:
            version = project.master_branch.latest_version

        result, data = Export.new_external_export(session = session,
                                                  project = project,
                                                  export_id = export_id,
                                                  version = version)

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

    project.generate_status = "complete"
    session.add(project)
