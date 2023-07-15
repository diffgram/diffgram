# OPENCORE - ADD
from methods.regular.regular_api import *

import tempfile
import threading

from shared.database.input import Input
from shared.database.source_control.working_dir import WorkingDir
from shared.database.video.video import Video

try:
    from shared.ingest.prioritized_item import PrioritizedItem
except:
    pass
from shared.regular import regular_methods, regular_log
from methods.input.upload import Upload
from shared.database.connection.connection import Connection
from sqlalchemy.orm.session import Session
from shared.helpers.permissions import get_session_string
from shared.url_generation import get_custom_url_supported_connector
from shared.system_startup.start_media_queue import process_media_queue_manager



@routes.route('/api/walrus/v1/project/<string:project_string_id>/input/packet',
              methods = ['POST'])
@Project_permissions.user_has_project(['admin', "Editor"])
@limiter.limit("20 per second")
def input_packet(project_string_id):
    """
    Import single packet

    1) Validate packet
    2) Send
    3) Return

    Question
        How are we deciding to return 400 bad request
        vs creating input with status regarding request?
            * Is the assumption that if we can determine an error
            we should do as soon as possible without creating it?
            * Or that if it's directly related to the spec list
            that's the criteria?
    """

    spec_list = [{'job_id': None},
                 {'file_id': None},
                 {'file_name': None},
                 {'mode': None},
                 {'directory_id': None},
                 {'original_filename': None},
                 {'raw_data_blob_path': None},
                 {'instance_list': {
                     "required": False,
                     "kind": list,

                 }},
                 {'text_data': None},
                 {'parent_file_id': {
                     "required": False,
                     "kind": int
                 }},
                 {'ordinal': {
                     "required": False,
                     "kind": int
                 }},
                 {'connection_id': {
                     "required": False,
                     "kind": int
                 }},
                 {'bucket_name': {
                     "required": False,
                     "kind": str
                 }},
                 {'blob_path': {
                     "required": False,
                     "kind": str
                 }},
                 {'type': None},
                 {'batch_id': None},
                 {"media": {
                     'default': {},
                     'kind': dict,
                 }
                 },
                 {"video_split_duration": {
                     'default': None,
                     'kind': int,
                 }
                 }
                 ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    # Careful, getting this from headers...
    # TODO: Remove usage of directory ID in headers.
    directory_id = request.headers.get('directory_id', None)
    if directory_id is None:
        directory_id = input['directory_id']

    if directory_id is None and input['mode'] != 'update':
        log["error"]['directory'] = "'directory_id' not supplied"
        return jsonify(log = log), 400

    # If we have at least one valid file type clear other errors.
    log['error'] = {}
    # Optional
    job_id = untrusted_input.get('job_id', None)
    mode = untrusted_input.get('mode', None)
    media_url = input['media'].get('url', None)
    media_type = input['media'].get('type', None)

    log["info"] = "Started processing"

    diffgram_input_id = None
    video_split_duration = input['video_split_duration']

    client_id = None
    if request.authorization:
        client_id = request.authorization.get('username', None)

    with sessionMaker.session_scope() as session:
        # Creates and input and puts it in the media processing queue.
        member = get_member(session)
        valid_file_data, log, file_id = validate_file_data_for_input_packet(
            session = session,
            input = input,
            project_string_id = project_string_id,
            log = log)
        if not valid_file_data:
            return jsonify(log = log), 400
        log = regular_log.default()
        connection_id_access_token = get_session_string()
        diffgram_input = enqueue_packet(project_string_id = project_string_id,
                                        session = session,
                                        media_url = media_url,
                                        media_type = media_type,
                                        job_id = job_id,
                                        file_id = file_id,
                                        directory_id = directory_id,
                                        instance_list = input.get('instance_list', None),
                                        parent_file_id = untrusted_input.get('parent_file_id', None),
                                        original_filename = input.get('original_filename', None),
                                        raw_data_blob_path = input.get('raw_data_blob_path', None),
                                        bucket_name = input.get('bucket_name', None),
                                        connection_id = input.get('connection_id', None),
                                        ordinal = input.get('ordinal', 0),
                                        video_split_duration = video_split_duration,
                                        frame_packet_map = untrusted_input.get('frame_packet_map', None),
                                        batch_id = untrusted_input.get('batch_id', None),
                                        type = input.get('type', None),
                                        text_data = input.get('text_data', None),
                                        enqueue_immediately = False,
                                        connection_id_access_token = connection_id_access_token,
                                        mode = mode,
                                        member = member)
        auth_api = None
        if client_id:
            auth_api = Auth_api.get(
                session = session,
                client_id = client_id)
        else:
            user = User.get(session)

        Event.new(
            session = session,
            kind = "input_from_packet",
            member_id = auth_api.member_id if auth_api else user.member.id,
            project_id = diffgram_input.project.id,
            description = str(diffgram_input.media_type),
            input_id = diffgram_input.id
        )

    log["success"] = True
    return jsonify(
        log = log,
        input_id = diffgram_input_id), 200


def enqueue_packet(project_string_id,
                   session,
                   media_url = None,
                   media_type = None,
                   file_id = None,
                   file_name = None,
                   job_id = None,
                   batch_id = None,
                   directory_id = None,
                   source_directory_id = None,
                   instance_list = None,
                   parent_file_id = None,
                   video_split_duration = None,
                   frame_packet_map = None,
                   remove_link = None,
                   add_link = None,
                   copy_instance_list = None,
                   commit_input = False,
                   task_id = None,
                   video_parent_length = None,
                   type = None,
                   task_action = None,
                   external_map_id = None,
                   connection_id = None,
                   bucket_name = None,
                   original_filename = None,
                   raw_data_blob_path = None,
                   external_map_action = None,
                   enqueue_immediately = False,
                   image_metadata: dict = {},
                   mode = None,
                   allow_duplicates = False,
                   auto_correct_instances_from_image_metadata = False,
                   extract_labels_from_batch = False,
                   connection_id_access_token = False,
                   member = None,
                   text_data: str = None,
                   ordinal: int = 0):
    """
            Creates Input() object and enqueues it for media processing
        Returns Input() object that was created
    :param project_string_id:
    :param session:
    :param media_url:
    :param media_type:
    :param file_id:
    :param file_name:
    :param job_id:
    :param batch_id:
    :param directory_id:
    :param source_directory_id:
    :param instance_list:
    :param parent_file_id:
    :param video_split_duration:
    :param frame_packet_map:
    :param remove_link:
    :param add_link:
    :param copy_instance_list:
    :param commit_input:
    :param task_id:
    :param video_parent_length:
    :param type:
    :param task_action:
    :param external_map_id:
    :param connection_id:
    :param bucket_name:
    :param original_filename:
    :param raw_data_blob_path:
    :param external_map_action:
    :param enqueue_immediately:
    :param image_metadata:
    :param mode:
    :param allow_duplicates:
    :param auto_correct_instances_from_image_metadata:
    :param extract_labels_from_batch:
    :param connection_id_access_token:
    :param do_enqueue:
    :param member:
    :return:
    """

    project = Project.get(session, project_string_id)
    if connection_id_access_token is not None:
        image_metadata['connection_id_access_token'] = connection_id_access_token

    diffgram_input = Input.new(
        image_metadata = image_metadata,
        file_id = file_id,
        task_id = task_id,
        batch_id = batch_id,
        ordinal = ordinal,
        parent_file_id = parent_file_id,
        raw_data_blob_path = raw_data_blob_path,
        video_parent_length = video_parent_length,
        remove_link = remove_link,
        add_link = add_link,
        text_data = text_data,
        copy_instance_list = copy_instance_list,
        external_map_id = external_map_id,
        original_filename = original_filename,
        external_map_action = external_map_action,
        connection_id = connection_id,
        bucket_name = bucket_name,
        task_action = task_action,
        mode = mode,
        project = project,
        media_type = media_type,
        type = type if type is not None else "from_url",
        url = media_url,
        video_split_duration = video_split_duration,
        auto_correct_instances_from_image_metadata = auto_correct_instances_from_image_metadata,
        allow_duplicates = allow_duplicates,
        member_created_id = member.id if member is not None else None,
        job_id = job_id,
        directory_id = directory_id,
        source_directory_id = source_directory_id,
        instance_list = instance_list,
        frame_packet_map = frame_packet_map,
    )

    session.add(diffgram_input)
    session.flush()

    if batch_id and extract_labels_from_batch:
        upload_tools = Upload(session = session, project = project, request = None, member = member)
        upload_tools.extract_instance_list_from_batch(input = diffgram_input,
                                                      input_batch_id = batch_id,
                                                      file_name = file_name)

    diffgram_input_id = diffgram_input.id

    if settings.PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY is True or enqueue_immediately:
        if commit_input:
            regular_methods.commit_with_rollback(session = session)
        item = PrioritizedItem(
            priority = 10000,  # individual frames have a priority here.
            input_id = diffgram_input_id,
            media_type = media_type)
        process_media_queue_manager.router(item)
    else:
        diffgram_input.processing_deferred = True  # Default

    return diffgram_input


def validate_input_from_text_data(input: dict, log: dict):
    if input.get('media') is None or input.get('media') == {}:
        log['error'] = {}
        log['error']['media'] = 'Provide media data. Needs to be {"type": str, "url": str<optional>}'

    if input.get('media') is not None and input['media'].get('type') is None:
        log['error'] = {}
        log['error']['media.type'] = 'Provide media type needs to be ["text"]'

    if input.get('text_data') is None:
        log['error'] = {}
        log['error']['text_data'] = 'Provide "text_data" as a string.'

    return log


def validate_input_from_blob_path(project: Project, input: dict, session: Session, log: dict):
    if input.get('connection_id') is None:
        log['error'] = {}
        log['error']['connection_id'] = 'Provide a connection ID'
    connection = Connection.get_by_id(session, id = input.get('connection_id'))

    if connection is None:
        log['error'] = {}
        log['error']['connection_id'] = 'Connection ID does not exist'
        return log

    connector, log = get_custom_url_supported_connector(session = session, log = log, connection_id = connection.id)
    if regular_log.log_has_error(log):
        return log

    if connection.project_id != project.id:
        log['error'] = {}
        log['error']['connection_id'] = 'Invalid Connection ID. Connection ID must belong to project'

    if input.get('bucket_name') is None:
        log['error'] = {}
        log['error']['bucket_name'] = 'Provide bucket name for blob'

    if input.get('media') is None or input.get('media') == {}:
        log['error'] = {}
        log['error']['media'] = 'Provide media data. Needs to be {"media_type": str, "url": str<optional>}'

    if input.get('media') is not None and input['media'].get('type') is None:
        log['error'] = {}
        log['error'][
            'media.type'] = 'Provide media type needs to be ["image", "video", "text", "audio", "csv", "sensor_fusion", "geo_tiff"]'
    if input.get('raw_data_blob_path') is None:
        log['error'] = {}
        log['error']['raw_data_blob_path'] = 'Provide raw_data_blob_path for blob'

    return log


def validate_file_data_for_input_packet(session, input, project_string_id, log):
    """
    Determines if payload has valid file data.
    Validation here goes like this:
        We expect either
        - file_id,
        - [media_url and media_type]
        - [file_name and directory_id]
        If none of these are completed error is returned.
    :param input:
    :param project_string_id:
    :param log:
    :return:
    """
    project = Project.get_by_string_id(session = session, project_string_id = project_string_id)
    if input.get('type') == 'from_blob_path':
        log = validate_input_from_blob_path(
            project = project,
            input = input,
            session = session,
            log = log
        )
        if regular_log.log_has_error(log):
            return False, log, None
        else:
            return True, log, None
    if input.get('type') == 'from_text_data':
        log = validate_input_from_text_data(
            input = input,
            log = log
        )
        if regular_log.log_has_error(log):
            return False, log, None
        else:
            return True, log, None
    valid_id = False
    valid_media_url = False
    valid_file_name = False
    if input.get('media'):
        media_url = input['media'].get('url', None)
        media_type = input['media'].get('type', None)
    else:
        media_url = None
        media_type = None

    file_id = None
    if input.get('file_id') is None and input.get('type') != 'from_text_data':
        # Validate Media URL Case
        if media_url is None:
            log['error'] = {}
            log["error"]["media_url"] = "url in media dict not supplied"
        else:
            if media_type is None:
                valid_media_url = False
                log['error'] = {}
                log["error"]["media_type"] = "type in media dict not supplied ['image', 'video']"
            else:
                valid_media_url = True

            if input.get('video_split_duration'):
                if input['video_split_duration'] > 180 or input['video_split_duration'] < 2:
                    valid_media_url = False
                    log["error"]["video_split_duration"] = "Duration must be between 2 and 180 seconds."

        if not valid_media_url:
            # Validate File name + directory
            file_name = input.get('file_name')
            directory_id = input.get('directory_id')
            if file_name is not None and directory_id is not None:
                file = File.get_by_name_and_directory(
                    session = session,
                    file_name = file_name,
                    directory_id = directory_id,
                )
                if file is not None and file.project_id == project.id:
                    valid_file_name = True
                    file_id = file.id
                else:
                    log['error'] = {}
                    log['error']['file_name'] = 'Please check that filename exists in given project and directory.'
            else:
                if directory_id is None:
                    log['error'] = {}
                    log['error']['directory_id'] = 'Provide directory_id along with file_name'
                if file_name is None:
                    log['error'] = {}
                    log['error']['file_name'] = 'Provide file_name along with directory_id'
    else:
        valid_id = True
        file_id = input['file_id']

    result = False
    if valid_media_url or valid_file_name or valid_id:
        result = True
        log['error'] = {}

    return result, log, file_id
