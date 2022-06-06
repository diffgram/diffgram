# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.data_tools_core import Data_tools
from shared.database.project import Project
from shared.export.export_create import create_new_export
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
        {"kind": str},
        {"source": str},
        {"file_comparison_mode": str},
        {"masks": bool},
        {"version_id": None},
        {"directory_id": None},
        {"job_id": None},
        {"task_id": None},
        {"return_type": None},
        {"wait_for_export_generation": {
            'default': False,
            'kind': bool
        }
        },
        {"ann_is_complete": {
            'default': None,
            'kind': bool
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)
        data, log = create_new_export(
            session = session,
            project = project,
            source = input['source'],
            task_id = input['task_id'],
            job_id = input['job_id'],
            directory_id = input['directory_id'],
            file_comparison_mode = input['file_comparison_mode'],
            kind = input['kind'],
            masks = input['masks'],
            ann_is_complete = input['ann_is_complete'],
            wait_for_export_generation = input['wait_for_export_generation'],
            return_type = input['return_type'],
            log = log,
            member_id = get_member(session = session).id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(data), 200

