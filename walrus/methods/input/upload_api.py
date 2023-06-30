from methods.regular.regular_api import *

from shared.database.input import Input
from shared.database.batch.batch import InputBatch
from shared.database.project import Project

from shared.data_tools_core import Data_tools
from shared.database.source_control.file import File
import traceback

from methods.input.upload import Upload


@routes.route('/api/walrus/project/<string:project_string_id>/upload/large',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ['admin', "Editor"],
    apis_user_list = ['api_enabled_builder',
                      'security_email_verified'])
@limiter.limit("4 per second")
def api_project_upload_large(project_string_id):
    """
    Error handling: Do we want a pattern of looking at logs
        or the input item... depends maybe both depends on context
    """

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)
        member = get_member(session)
        upload = Upload(
            session = session,
            project = project,
            request = request,
            member = member)

        upload.route_from_unique_id()
        if len(upload.log["error"].keys()) >= 1:
            return jsonify(log = upload.log), 400

        upload.process_chunk(
            request = upload.request,
            input = upload.input)

        if len(upload.log["error"].keys()) >= 1:
            return jsonify(log = upload.log), 400

        more_chunks_expected: bool = int(upload.dzchunkindex) + 1 != int(upload.dztotalchunkcount)

        if more_chunks_expected is False and upload.input is not None:
            regular_methods.commit_with_rollback(session)
            upload.start_media_processing(input = upload.input)

        return jsonify(success = True), 200


@routes.route('/api/walrus/v1/project/<string:project_string_id>/input/from_local',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ['admin', "Editor"],
    apis_user_list = ['api_enabled_builder',
                      'security_email_verified'])
def api_project_input_from_local(project_string_id):
    try:
        json_parsed = json.loads(request.form.get('json'))
    except:
        temp_log = regular_log.default_api_log()
        temp_log["error"]["input"] = "Expecting a key 'json' in form request."
        return jsonify(log = temp_log), 400

    spec_list = [
        {"directory_id": {
            'default': None,
            'kind': int,
            'required': False
        }},
        {"parent_file_id": {
            'default': None,
            'kind': int,
            'required': False
        }},
        {'ordinal': {
            "required": False,
            "kind": int
        }},
        {"instance_list": {
            'default': None,
            'kind': list,
            'allow_empty': True,
            'required': False
        }
        },
        {"frame_packet_map": {  # WIP
            'default': None,
            'kind': dict,
            'required': False
        },
        }
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list,
        untrusted_input = json_parsed)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        directory = WorkingDir.get_with_fallback(
            session = session,
            project = project,
            directory_id = input.get('directory_id')
        )
        if directory is False:
            log['error'] = f"Bad directory_id: {input.get('directory_id')}"
            return jsonify(log = log), 400

        file = request.files.get('file')
        if not file:
            log['error'] = "No files"
            return jsonify(log = log), 400

        result, log, input = Upload.input_from_local(
            session = session,
            log = log,
            project_string_id = project_string_id,
            file = file,
            directory_id = directory.id,
            parent_file_id = input.get('parent_file_id'),
            http_input = input,
            ordinal = input.get('ordinal', 0),
            )

        if result is not True:
            return jsonify(
                log = log,
                input = input.serialize()), 400

        if result is True:
            log['success'] = True
            return jsonify(
                log = log,
                input = input.serialize(),
                file = input.file.serialize()), 200
