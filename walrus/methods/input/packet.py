# OPENCORE - ADD
from methods.regular.regular_api import *

import tempfile
import threading

from shared.database.input import Input
from shared.database.source_control.working_dir import WorkingDir
from shared.database.video.video import Video

try:
    from methods.input.process_media import PrioritizedItem
    from methods.input.process_media import add_item_to_queue
except:
    pass
from shared.regular import regular_methods


def enqueue_packet(project_string_id,
                   session,
                   media_url=None,
                   media_type=None,
                   file_id=None,
                   job_id=None,
                   batch_id=None,
                   directory_id=None,
                   source_directory_id=None,
                   instance_list=None,
                   video_split_duration=None,
                   frame_packet_map=None,
                   remove_link=None,
                   add_link=None,
                   copy_instance_list=None,
                   commit_input=False,
                   task_id=None,
                   video_parent_length=None,
                   type=None,
                   task_action=None,
                   external_map_id=None,
                   external_map_action=None,
                   enqueue_immediately=False,
                   mode=None,
                   allow_duplicates=False):
    """
        Creates Input() object and enqueues it for media processing
        Returns Input() object that was created
    :param packet_data:
    :return:
    """
    diffgram_input = Input()

    diffgram_input.file_id = file_id
    diffgram_input.task_id = task_id
    diffgram_input.batch_id = batch_id
    diffgram_input.video_parent_length = video_parent_length
    diffgram_input.remove_link = remove_link
    diffgram_input.add_link = add_link
    diffgram_input.copy_instance_list = copy_instance_list
    diffgram_input.external_map_id = external_map_id
    diffgram_input.external_map_action = external_map_action
    diffgram_input.task_action = task_action
    diffgram_input.mode = mode
    diffgram_input.project = Project.get(session, project_string_id)
    diffgram_input.media_type = media_type
    diffgram_input.type = "from_url"
    diffgram_input.url = media_url
    diffgram_input.video_split_duration = video_split_duration
    diffgram_input.allow_duplicates = allow_duplicates

    if instance_list:
        diffgram_input.instance_list = {}
        diffgram_input.instance_list['list'] = instance_list

    if frame_packet_map:
        diffgram_input.frame_packet_map = frame_packet_map
    # print(diffgram_input.frame_packet_map)

    session.add(diffgram_input)
    session.flush()

    # Expect temp dir to be None here.
    # because each machine should assign it's own temp dir
    # Something else to consider for future here!

    # Once this is part of input, it will be smoothly handled at right time as part of
    # processing queue
    diffgram_input.job_id = job_id

    # Process media handles checking if the directory id is valid
    diffgram_input.directory_id = directory_id
    diffgram_input.source_directory_id = source_directory_id

    diffgram_input_id = diffgram_input.id

    queue_limit = 0
    if media_type == "image":
        queue_limit = 30  # 50
    if media_type == "video":
        queue_limit = 1


    if settings.PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY is True or enqueue_immediately:
  
        print('diffgram_input_id', diffgram_input_id)
        if commit_input:
            regular_methods.commit_with_rollback(session = session)
        item = PrioritizedItem(
            priority=10000,  # individual frames have a priority here.
            input_id=diffgram_input_id,
            media_type=media_type)
        add_item_to_queue(item)
    else:
        diffgram_input.processing_deferred = True   # Default  

    return diffgram_input


@routes.route('/api/walrus/v1/project/<string:project_string_id>/input/packet',
              methods=['POST'])
@Project_permissions.user_has_project(['admin', "Editor"])
@limiter.limit("3 per second, 320 per minute, 3000 per day")
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
                 {'mode': None},
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

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # log = {"success" : False, "errors" : []}

    # Careful, getting this from headers...
    directory_id = request.headers.get('directory_id', None)
    if directory_id is None:
        log["error"]['directory'] = "'directory_id' not supplied"
        return jsonify(log=log), 400

    media_url = input['media'].get('url', None)
    media_type = input['media'].get('type', None)

    if input['file_id'] is None:
        if media_url is None:
            log["error"]["media"] = "url in media dict not supplied"
            return jsonify(log=log), 400

        if media_type is None:
            log["error"]["media"] = "type in media dict not supplied ['image', 'video']"
            return jsonify(log=log), 400

        if input['video_split_duration']:
            if input['video_split_duration'] > 180 or input['video_split_duration'] < 2:
                log["error"]["video_split_duration"] = "Duration must be between 2 and 180 seconds."
                return jsonify(log=log), 400

    # Optional
    job_id = untrusted_input.get('job_id', None)
    mode = untrusted_input.get('mode', None)

    log["info"] = "Started processing"

    # QUESTION how early do we want to record input here?
    # ie do we want to record 400 type errors? or stictly after we
    # have a "valid" starting point

    # Do we actually want to use a long running operation here?
    # If we do can't pass input directly.... sigh
    # need to revist if want to do this using imediate mode or not

    diffgram_input_id = None
    video_split_duration = input['video_split_duration']

    client_id = request.authorization.get('username', None)
    with sessionMaker.session_scope() as session:
        # Creates and input and puts it in the media processing queue.
        diffgram_input = enqueue_packet(project_string_id=project_string_id,
                                        session=session,
                                        media_url=media_url,
                                        media_type=media_type,
                                        job_id=job_id,
                                        file_id=input['file_id'],
                                        directory_id=directory_id,
                                        instance_list=untrusted_input.get('instance_list', None),
                                        video_split_duration=video_split_duration,
                                        frame_packet_map=untrusted_input.get('frame_packet_map', None),
                                        mode=mode)

        auth_api = Auth_api.get(
            session=session,
            client_id=client_id)

        Event.new(
            session=session,
            kind="input_from_packet",
            member_id=auth_api.member_id,
            project_id=diffgram_input.project.id,
            description=str(diffgram_input.media_type),
            input_id=diffgram_input.id
        )

    log["success"] = True
    return jsonify(
        log=log,
        input_id=diffgram_input_id), 200
