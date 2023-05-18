# OPENCORE - ADD
from shared.regular.regular_api import *
from shared.regular import regular_methods

import tempfile

from shared.database.input import Input
from shared.database.source_control.working_dir import WorkingDir
from shared.database.video.video import Video

on_walrus = True

try:
    from walrus.methods.input.process_media import PrioritizedItem
    from walrus.methods.input.process_media import add_item_to_queue
    from walrus.methods.input.upload import Upload
except:
    try:
        from methods.input.process_media import PrioritizedItem
        from methods.input.process_media import add_item_to_queue
        from methods.input.upload import Upload
    except:
        on_walrus = False


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
                   original_filename = None,
                   external_map_action = None,
                   enqueue_immediately = False,
                   action_trigger_id = None,
                   workflow_trigger_id = None,
                   image_metadata = {},
                   mode = None,
                   allow_duplicates = False,
                   auto_correct_instances_from_image_metadata = False,
                   extract_labels_from_batch = False,
                   member = None):
    """
        Creates Input() object and enqueues it for media processing
        Returns Input() object that was created
    :param packet_data:
    :return:
    """
    diffgram_input = Input()
    project = Project.get(session, project_string_id)
    diffgram_input.file_id = file_id
    diffgram_input.action_trigger_id = action_trigger_id
    diffgram_input.workflow_trigger_id = workflow_trigger_id
    diffgram_input.image_metadata = image_metadata
    diffgram_input.auto_correct_instances_from_image_metadata = auto_correct_instances_from_image_metadata
    diffgram_input.task_id = task_id
    diffgram_input.batch_id = batch_id
    diffgram_input.video_parent_length = video_parent_length
    diffgram_input.remove_link = remove_link
    diffgram_input.add_link = add_link
    diffgram_input.copy_instance_list = copy_instance_list
    diffgram_input.external_map_id = external_map_id
    diffgram_input.original_filename = original_filename
    diffgram_input.external_map_action = external_map_action
    diffgram_input.task_action = task_action
    diffgram_input.mode = mode
    diffgram_input.project = project
    diffgram_input.media_type = media_type
    diffgram_input.type = "from_url"
    diffgram_input.url = media_url
    diffgram_input.video_split_duration = video_split_duration
    diffgram_input.allow_duplicates = allow_duplicates
    diffgram_input.member_created = member
    if instance_list:
        diffgram_input.instance_list = {}
        diffgram_input.instance_list['list'] = instance_list

    if frame_packet_map:
        diffgram_input.frame_packet_map = frame_packet_map
    # print(diffgram_input.frame_packet_map)

    session.add(diffgram_input)
    session.flush()

    if settings.DIFFGRAM_SERVICE_NAME == 'walrus':
        if batch_id and extract_labels_from_batch:
            upload_tools = Upload(session = session, project = project, request = None, member = member)
            upload_tools.extract_instance_list_from_batch(input = diffgram_input,
                                                          input_batch_id = batch_id,
                                                          file_name = file_name)
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

    # Temporary workaround until new Rabbit MQ implmentation for walrus
    if on_walrus:

        if settings.PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY is True or enqueue_immediately:
            if commit_input:
                regular_methods.commit_with_rollback(session = session)
            item = PrioritizedItem(
                priority = 10000,  # individual frames have a priority here.
                input_id = diffgram_input_id,
                media_type = media_type)
            add_item_to_queue(item)
        else:
            diffgram_input.processing_deferred = True  # Default
    else:
        diffgram_input.processing_deferred = True  # Default

    return diffgram_input

