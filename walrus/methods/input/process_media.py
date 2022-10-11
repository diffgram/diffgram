from methods.regular.regular_api import *
from methods.video.video import New_video

try:
    from methods.video.video_preprocess import Video_Preprocess
except Exception as exception:
    print("Fail, Video_Preprocess: Could not import", exception)

import requests
import threading
import tempfile
import csv
import gc
import shutil
from urllib.parse import urlsplit
from random import randrange

from werkzeug.utils import secure_filename

from imageio import imwrite
from imageio import imread
from shared.image_tools import imresize

from shared.database.user import UserbaseProject
from shared.utils.memory_checks import check_and_wait_for_memory
from shared.database.input import Input
from shared.database.video.video import Video
from shared.database.image import Image
from shared.annotation import Annotation_Update
from shared.database.video.sequence import Sequence
from shared.utils.task import task_complete
from shared.data_tools_core import Data_tools

global Update_Input
from methods.input.input_update import Update_Input
from shared.database.model.model_run import ModelRun
from shared.database.audio.audio_file import AudioFile
from shared.database.model.model import Model
from shared.utils import job_dir_sync_utils
from shared.database.task.job.job import Job
from tenacity import retry, wait_random_exponential, stop_after_attempt
from shared.database.text_file import TextFile
from shared.database.task.job.job_working_dir import JobWorkingDir
from shared.model.model_manager import ModelManager
import traceback
from shared.utils.source_control.file.file_transfer_core import perform_sync_events_after_file_transfer
from methods.sensor_fusion.sensor_fusion_file_processor import SensorFusionFileProcessor
from methods.geotiff.GeoTiffProcessor import GeoTiffProcessor
import numpy as np
from shared.regular.regular_log import log_has_error
import os
from shared.feature_flags.feature_checker import FeatureChecker
from shared.utils.singleton import Singleton
from methods.text_data.text_tokenizer import TextTokenizer
from shared.utils.instance.transform_instance_utils import rotate_instance_dict_90_degrees
from shared.ingest.allowed_ingest_extensions import images_allowed_file_names, \
    sensor_fusion_allowed_extensions, \
    geo_tiff_allowed_extensions, \
    videos_allowed_file_names, \
    text_allowed_file_names, \
    audio_allowed_file_names, \
    csv_allowed_file_names, \
    existing_instances_allowed_file_names

data_tools = Data_tools().data_tools

STOP_PROCESSING_DATA = False


@dataclass(order = True)
class PrioritizedItem:
    # https://diffgram.com/docs/prioritizeditem
    priority: int
    input_id: int = field(compare = False, default = None)
    input: int = field(compare = False, default = None)
    file_is_numpy_array: bool = field(compare = False, default = False)
    raw_numpy_image: Any = field(compare = False, default = None)
    video_id: Any = field(compare = False, default = None)
    video_parent_file: Any = field(compare = False, default = None)
    frame_number: Any = field(compare = False, default = None)
    global_frame_number: Any = field(compare = False, default = None)
    frame_completion_controller: Any = None
    total_frames: int = 0
    num_frames_to_update: int = 0
    media_type: str = None


def process_media_unit_of_work(item):
    from methods.input.process_media_queue_manager import process_media_queue_manager
    with sessionMaker.session_scope_threaded() as session:

        process_media = Process_Media(
            session = session,
            input_id = item.input_id,
            input = item.input,
            item = item)

        if settings.PROCESS_MEDIA_TRY_BLOCK_ON is True:
            try:

                process_media_queue_manager.add_item_to_processing_list(item)
                process_media.main_entry()
                process_media_queue_manager.remove_item_from_processing_list(item)

            except Exception as e:
                logger.error(f"[Process Media] Main failed on {item.input_id}")
                logger.error(str(e))
                logger.error(traceback.format_exc())
                process_media_queue_manager.remove_item_from_processing_list(item)
        else:
            process_media_queue_manager.add_item_to_processing_list(item)
            process_media.main_entry()
            process_media_queue_manager.remove_item_from_processing_list(item)


# REMOTE queue
def start_queue_check_loop(VIDEO_QUEUE, FRAME_QUEUE):
    # https://diffgram.com/docs/remote-queue-start_queue_check_loop
    from methods.input.process_media_queue_manager import process_media_queue_manager
    if settings.PROCESS_MEDIA_REMOTE_QUEUE_ON == False:
        return

    add_deferred_items_time = 5

    while True:
        time.sleep(add_deferred_items_time)
        if process_media_queue_manager.STOP_PROCESSING_DATA:
            logger.warning('Rejected Item: processing, data stopped. Waiting for termination...')
            break

        check_and_wait_for_memory(memory_limit_float = 75.0)

        logger.info("[Media Queue Heartbeat]")
        try:
            add_deferred_items_time = check_if_add_items_to_queue(add_deferred_items_time, VIDEO_QUEUE, FRAME_QUEUE)
        except Exception as exception:
            logger.info(f"[Media Queue Failed] {str(exception)}")
            add_deferred_items_time = 30  # reset


def check_if_add_items_to_queue(add_deferred_items_time, VIDEO_QUEUE, FRAME_QUEUE):
    # https://diffgram.com/docs/remote-queue-check_if_add_items_to_queue

    queue_limit = 1
    if VIDEO_QUEUE.qsize() >= queue_limit:
        return add_deferred_items_time

    if FRAME_QUEUE.qsize() >= 30:
        logger.info(f"FRAME QUEUE LIMIT {str(FRAME_QUEUE.qsize())}")
        return add_deferred_items_time

    with sessionMaker.session_scope_threaded() as session:

        try:
            update_input = Update_Input(session = session).automatic_retry()
        except Exception as exception:
            logger.error(f"Couldn't find Update_Input {str(exception)}")
            return 30

        input = session.query(Input).with_for_update(skip_locked = True).filter(
            Input.processing_deferred == True,
            Input.archived == False,
            Input.status != 'success'
        ).first()

        if input is None:
            add_deferred_items_time += 30
            add_deferred_items_time = min(add_deferred_items_time, 200)
            return add_deferred_items_time

        add_deferred_items_time = 3  # reset, fast process if None available
        # we trust if video queue is busy it will be handled and not reach to this point

        session.add(input)
        input.processing_deferred = False

        item = PrioritizedItem(
            priority = 100,  # 100 is current default priority
            input_id = input.id)
        add_item_to_queue(item)
        logger.info(f"{str(input.id)} Added to queue.")

        return add_deferred_items_time


# https://diffgram.com/docs/process-media-local-worker-queues


def add_item_to_queue(item):
    # https://diffgram.com/docs/add_item_to_queue
    from methods.input.process_media_queue_manager import process_media_queue_manager
    if item.media_type and item.media_type == "video":
        process_media_queue_manager.VIDEO_QUEUE.put(item)
    else:
        wait_until_queue_pressure_is_lower(
            queue = process_media_queue_manager.FRAME_QUEUE,
            limit = process_media_queue_manager.frame_threads * 2,
            check_interval = 1)
        process_media_queue_manager.FRAME_QUEUE.put(item)


def wait_until_queue_pressure_is_lower(queue, limit, check_interval = 1):
    while True:
        if queue.qsize() < limit:
            return True
        else:
            logger.warn(f"Queue Presure Too High: {str(queue.qsize())} size is above limit of {limit} ")
            time.sleep(check_interval)


def process_media_queue_worker(queue, queue_type, frame_queue_lock, video_queue_lock):
    queue_lock = None
    if queue_type == 'frame':
        queue_lock = frame_queue_lock
    elif queue_type == 'video':
        queue_lock = video_queue_lock
    else:
        logger.error('Invalid queue type')
        return
    while True:
        process_media_queue_getter(queue, queue_lock)


def process_media_queue_getter(queue, queue_lock):
    # https://diffgram.com/docs/process_media_queue_getter
    queue_lock.acquire()
    if not queue.empty():
        item = queue.get()
        queue_lock.release()
        process_media_unit_of_work(item)
        queue.task_done()
    else:
        queue_lock.release()
        time.sleep(0.1)


class Process_Media():
    """
    Basic process of using this is to call init with session and:
    * project or project_id
    * input or input_id

    Generally expect
        * prefer object (ie project), the id option (ie project_id) is for threading
        * Input class to already be "setup" with useful info before calling this
        * That the file is "available" either in memory as a numpy array
         or in a temporary directory. if the file is from a url
         we attempt to download it first.

    Expected call methods
        * main_entry()
        * process_one_image_file()
        * process_url()

    On recursion and threads
        * we expect main_entry() can be called recursively, for example
        from process_csv
        * we can create instances of Process_Media to use with threads
        or for recursive

    EXAMPLE use:

    process_media = Process_Media(
        session = session,
        member = None,
        input_id = input_id)

    process_media.main_entry()

    (See upload.py)

    main_entry is generally when the file type or method is unknown
    for example, from the UI where the user can upload many types

    the other methods are meant to be used in conjunction with other classes
    ie process_one_image_file() for use with video
    or process_url for use with prediction

    As we progress from just "get the files in there"
    to "do stuff with the files" and "pull from API / other sources" this
    class can expand.

    CAUTION
        input_id is not guaranteed to be available
        and if Input object is passed of some types (currently == frame),
        then we do NOT commit it and do not expect
        input.id to be available either.

    """

    def __init__(self,
                 session,
                 member = None,
                 project: Project = None,
                 project_id: int = None,
                 org = None,
                 raw_file = None,
                 input_id: int = None,
                 input: Input = None,
                 item = None
                 ):

        # Assign default item since we currently
        # define defaults for paremters below in the item class
        # input_id is not used from item at this stage
        # which is confusing but works for now I guess?
        # (but is required on PrioritizedItem construction.) sigh
        # This is more of a "hold over from switching / immediate mode")

        if item is None:
            item = PrioritizedItem(
                priority = 100,
                input_id = None)

        self.video_id = item.video_id
        self.video_parent_file = item.video_parent_file
        self.file_is_numpy_array = item.file_is_numpy_array
        self.raw_numpy_image = item.raw_numpy_image
        self.frame_number = item.frame_number
        self.total_frames = item.total_frames
        self.num_frames_to_update = item.num_frames_to_update
        self.frame_completion_controller = item.frame_completion_controller

        self.raw_file = raw_file

        self.input = input
        self.input_id = input_id

        # file is accessible through self.input.file

        self.session = session
        self.sequence_map = {}
        self.member = member
        self.project = project  # This get set from self.input in main_entry()
        self.project_id = project_id
        self.org = org

        # It creates it's own log for each run...

        self.log = regular_log.default()
        # Question, if not running from http do we still follow same log pattern?
        # If so we should build log from Regular method
        # This also feels confused with the input.status and input.status text

        # TODO get limit from org/project/user etc.
        self.directory_file_count_limit = 90000

        # for directory_id see self.input.directory_id

        # Question, for video, do we want to record
        # A per frame input class???
        # That could be confusing.

        self.allow_csv = True

        if self.input and not isinstance(self.input, Input):
            raise Exception("input should be class Input object. Use input_id for ints")

    ### TODO move these other main entry things over to init

    @retry(wait = wait_random_exponential(multiplier = 1, max = 5),
           stop = stop_after_attempt(4))
    def get_input_with_retry(self):
        """
        If we already have a valid input object we skip this
            else get it from DB.

            In general the assumption for deferred processing
            is that we won't have the object.
            If processing is using the input "pattern"
            but needs local (ie 'frame') type
            then it can have it.
        """

        if self.input is None:

            self.input = Input.get_by_id(
                session = self.session,
                id = self.input_id)

            # Oracle if get_by_id() failed
            # Do we want to log this somewhere on 'final' failure?
            if self.input is None:
                raise Exception('Input not Found.')

        if not self.input.update_log:
            self.input.update_log = regular_log.default()

    def main_entry(self):
        """

        input.status_text has error message if applicable
        """

        start_time = time.time()

        check_and_wait_for_memory(memory_limit_float = 75.0)

        ### Warm up
        self.get_input_with_retry()

        # We update this here because
        # it may be set to retry, but not start processing for a while
        # So we only want to set this time when we start processing it
        self.input.time_last_attempted = start_time

        # Jan 20, 2020, TODO can we safely remove self.project

        self.project = self.input.project

        """
        Context that for detached from session processing
        (ie media_type == 'frame'), if we try to access input.project.id
        that will do a refresh from the session which will fail
        because we are purposely not attaching input

        """
        self.project_id = self.input.project_id
        if self.project is None:
            self.project = Project.get_by_id(
                session = self.session,
                id = self.project_id)

        if self.input.allow_csv:
            self.allow_csv = self.input.allow_csv

        # Advantage of doing this here is then it's set
        # For all ways a flow can come in...
        # Not clear if this is best place to set this.

        if self.input.mode == "flow":
            # Get directory from flow
            self.input.directory = self.input.action_flow.directory

        self.input.status = "processing"

        self.try_to_commit()

        if self.input.mode == "copy_file":
            self.__copy_file()
            # Important!
            # We are exiting main loop here
            return
        if self.input.mode == "update":
            self.__update_existing_file(file = self.input.file)
            # Important!

            # We are exiting main loop here
            if len(self.log["error"].keys()) >= 1:
                logger.error(f"Error updating instances: {str(self.log['error'])}")
                return

            return
        if self.input.mode == "update_with_existing":  # existing instances
            self.__update_existing_file(file = self.input.file,
                                        init_existing_instances = True)
            # Important!
            # We are exiting main loop here
            if len(self.log["error"].keys()) >= 1:
                logger.error(f"Error updating instances: {str(self.log['error'])}")
                return

            return

        if self.input.type not in ["from_url", "from_video_split"]:
            # For those types we populate the filename from URL later in process
            # `from_resumable` (eg from UI), we already have the name, so do check here
            # `from_url` we "build" name later, so if we check here original_filename is None.
            if self.__file_does_not_exist_in_target_directory() is False:
                return False

        if self.input.media_type != "frame":
            """
            Causing Instance <Project at 0x> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: http://sqlalche.me/e/bhk3)
            if we try to get it on a "Detached" session

            We don't appear to need the working dir for frame processing
            This block should probably be it's own function

            """
            # Why are we getting working_dir here?
            # Why not just use it from input.directory?
            self.working_dir = WorkingDir.get_with_fallback(
                session = self.session,
                project = self.project,
                directory_id = self.input.directory_id)

            # Careful to not leak directory information through this
            if self.working_dir is False or self.working_dir is None:
                self.input.status = "failed"
                self.input.status_text = "Invalid directory permission."
                self.input.invalid_directory_permission = True
                return False

            self.working_dir_id = self.working_dir.id  # cache for threading workaround

            if self.input.directory_id is None:
                self.input.directory_id = self.working_dir_id

            check_limits_result = self.check_limits()
            if check_limits_result is False:
                return False

        if self.input.type in ["from_resumable",
                               "from_url",
                               "from_video_split",
                               "from_sensor_fusion_json",
                               "from_geo_tiff",
                               "from_geo_tiff_json",
                               "ui_wizard"]:

            download_result = self.download_media()

            # careful we expect keys available here ie
            # log['error']['status_text']
            if len(self.log["error"].keys()) >= 1:
                logger.error(f"Error downloading media: {str(self.log['error'])}")
                self.input.update_log['error'] = self.log['error']
                return False

        if self.input.media_type == "video":
            """
            If video_was_split is True
                We return early becasue we don't want 
                To actually process the "root" video file.
                beyond what the split into clips function does

                I'm a little wary of calling it "was_split"
                as that operation could fail... maybe another name...
            Else:
                 We want to try processing the file by itself

            This whole chain still feels waaay to complicated...
             but we need an exit condition potentially here right... 
            Still something that could be improved...
            """
            self.input.video_was_split = self.split_video_into_clips()

            if self.input.video_was_split is True:
                self.try_to_commit()
                return True

        ###

        ### Main
        self.check_free_tier_limits()

        if log_has_error(self.log):
            return False

        self.route_based_on_media_type()

        ###

        self.try_to_commit()

        if not self.input:
            return True

        if log_has_error(self.log):
            return False

        process_instance_result = self.process_existing_instance_list()

        self.may_attach_to_job()

        self.update_jobs_with_attached_dirs()

        end_time = time.time()
        self.log['info']['run_time'] = end_time - start_time

        return True

    def __file_does_not_exist_in_target_directory(self):
        """
        Context
            1) A user uploading same data twice.
            2) We assume this doesn't fire on "update" approaches (based on where it 
            is in process_media execution

        Overrides options
            1) Set input.allow_duplicates = True
            2) Remove the file from the directory and retry (can use literal retry process,
            or just a fresh input)
            3) Target a different dataset
        """

        if self.input.allow_duplicates is True:
            return True

        existing_file_list = WorkingDirFileLink.file_list(
            session = self.session,
            working_dir_id = self.input.directory_id,
            original_filename = self.input.original_filename,
            original_filename_match_type = None
        )
        if existing_file_list:
            self.input.status = "failed"
            self.input.status_text = f"Filename {self.input.original_filename} Already Exists in Dir. Existing ID is:{str(existing_file_list[0].id)}"
            self.input.update_log = {'error': {
                'existing_file_id': existing_file_list[0].id}
            }
            return False

        return True

    def __copy_video(self):

        logger.debug(f"Copying Video {self.input.file_id}")

        self.input.newly_copied_file = File.copy_file_from_existing(
            session = self.session,
            working_dir = self.input.directory,
            orginal_directory_id = self.input.source_directory_id,
            existing_file = self.input.file,
            copy_instance_list = False,
            log = self.input.update_log,
            add_link = True,
            remove_link = False,
            flush_session = True,
            defer_copy = False,
            batch_id = self.input.batch_id
        )

        if self.input.copy_instance_list is False:
            # For declaring success on the video file when no frames are available (i.e no instances)
            self.declare_success(input = self.input)
            return

        # COPY INSTANCES, Sequences, and Frames
        new_video = New_video(
            session = self.session,
            project = self.project,
            input = self.input
        )
        new_video.add_sequence_map_to_input(
            source_video_parent_file = self.input.file,
            destination_video_parent_file_id = self.input.newly_copied_file.id)

        # We commit session to ensure that when pushing the frames to queue below (that will be on multiple threads)
        # they have access to the Sequences ID's on the DB.
        self.try_to_commit()

        # Push all the frames to the Queue
        frames_list = new_video.push_frames_for_copy_to_queue(
            source_video_parent_file_id = self.input.file_id,
            destination_video_parent_file_id = self.input.newly_copied_file.id)

        if len(frames_list) == 0:
            # For declaring success on the video file when no frames are available (i.e no instances)
            self.declare_success(input = self.input)

    def __copy_frame(self):

        file = File.get_by_id(self.session, self.input.file_id)

        # The frame input has copies of this so we don't have to get parent

        new_file = File.copy_file_from_existing(
            session = self.session,
            working_dir = None,  # avoid detached session
            working_dir_id = self.input.directory_id,
            existing_file = file,
            copy_instance_list = self.input.copy_instance_list,
            add_link = self.input.add_link,  # Not sure about making this dynamic
            remove_link = self.input.remove_link,
            sequence_map = self.input.sequence_map,
            previous_video_parent_id = self.input.parent_file_id,
            flush_session = True,
        )
        self.frame_completion_controller.mark_frame_complete(self.frame_number)
        # Update Percent of parent input
        self.video_status_updates()

        # Should this be part of "declare success?
        # Or use get_parent_with_retry()
        if self.frame_number == self.total_frames:
            # Perform sync operations
            parent_input = self.input.parent_input(self.session)
            perform_sync_events_after_file_transfer(
                session = self.session,
                source_directory = parent_input.source_directory,
                destination_directory = parent_input.directory,
                log = self.log,
                log_sync_events = True,
                transfer_action = 'copy',
                file = parent_input.file,
                member = self.member,
                new_file = parent_input.newly_copied_file,
                defer_sync = False,
                sync_event_manager = None,
            )

        return new_file

    def __copy_image(self):
        logger.debug(f"Copying Image {self.input.file_id}")

        self.input.newly_copied_file = File.copy_file_from_existing(
            session = self.session,
            working_dir = None,
            working_dir_id = self.input.directory_id,
            existing_file = self.input.file,
            copy_instance_list = self.input.copy_instance_list,
            add_link = self.input.add_link,
            remove_link = self.input.remove_link,
            sequence_map = None,
            previous_video_parent_id = None,
            flush_session = True
        )

        self.declare_success(self.input)
        # Perform sync operations
        source_dir = WorkingDir.get_by_id(self.session, self.input.source_directory_id)
        dest_dir = WorkingDir.get_by_id(self.session, self.input.directory_id)
        perform_sync_events_after_file_transfer(
            session = self.session,
            source_directory = None,  # We just provide destination directory to attach incoming dir to task.
            destination_directory = dest_dir,
            log = self.log,
            log_sync_events = True,
            transfer_action = 'copy',
            file = self.input.file,
            member = self.member,
            new_file = self.input.newly_copied_file,
            defer_sync = False,
            sync_event_manager = None,
        )
        return self.input.newly_copied_file

    def __copy_file(self):
        # Prep work
        if self.input.media_type == "video":
            logger.info(f"Starting Sequenced Copy from File {self.input.file.id}")
            # Get the sequence_map.
            self.__copy_video()
            return
        elif self.input.media_type == 'frame':
            self.__copy_frame()
        elif self.input.media_type == 'image':
            self.__copy_image()

    def __update_existing_file(self,
                               file,
                               init_existing_instances = False):

        # Prep work
        if file:
            self.input.media_type = file.type
            # not sure about this, we make assumptions about file type downstream

        if self.input.media_type is None:
            # Even if the file will *eventually* be valid, if we don't know the media type
            # then we can't reasonably process the update.
            # https://github.com/diffgram/training_data/pull/269
            self.log['error']['media_type'] = "media_type undefined. This may be a timing issue. \
                    Try including instances in single request, or waiting for file to finish processing before sending."
            return False
        try:
            self.populate_new_models_and_runs()

            # TODO what other input keys do we need to update (ie this assumes images etc)
            if file and self.input.media_type == "video":
                logger.debug("Parent Video File Update")
                self.__update_existing_video()  # Maybe should be a strategy operation
                return

            elif file and self.input.media_type == 'text':
                self.process_existing_instance_list(
                    init_existing_instances = init_existing_instances)
            else:
                process_instance_result = self.process_existing_instance_list(
                    init_existing_instances = init_existing_instances)
                logger.debug(("Image or Frame File Update"))

                if file and file.frame_number:
                    logger.info(f"{file.frame_number}, {self.input.video_parent_length}")

                if process_instance_result is True and self.input.media_type == 'frame':
                    self.__update_parent_video_at_last_frame()

            # TODO first video case (otherwise then goes in frame processing flow)
            if self.input.media_type in ["image", "text"] and self.input.status != "failed":
                self.declare_success(input = self.input)
        except Exception as e:
            logger.error(traceback.format_exc())
            self.input.status = 'failed'
            self.input.description = str(e)
            self.input.update_log = {'error': traceback.format_exc()}
            self.log['error']['update_instance'] = str(e)
            self.log['error']['traceback'] = traceback.format_exc()
            if self.input.media_type == 'frame':
                self.proprogate_frame_instance_update_errors_to_parent(self.log)

    def __update_parent_video_at_last_frame(self):
        # Last frame
        # In the update context input.video_parent_length = self.highest_frame_encountered
        if self.input.frame_number == self.input.video_parent_length:
            # Assumes frames are put in priority queue in frame order.
            # See determine_unique_sequences_from_external() for how this is derived
            logger.info("Last Frame Update")
            time.sleep(4)  # in case this worker is ahead of another
            logger.info("Updating Sequences")
            self.update_sequences()

            # We assume if we get to this stage it was successful?
            parent_input = self.get_parent_input_with_retry()

            self.__toggle_flags_from_input(input = parent_input)
            self.declare_success(input = parent_input)
            self._add_input_to_session(parent_input)

    def __toggle_flags_from_input(self, input: Input):
        if not input.task:
            return

        if input.task_action == 'complete_task':
            result, new_file = task_complete.task_complete(
                session = self.session,
                task = input.task,
                new_file = input.file,
                project = self.project,
                member = self.member)

    def __update_existing_video(self):

        global New_video  # important
        from methods.video.video import New_video

        if not self.input.frame_packet_map:
            self.input.update_log['error'][
                'frame_packet_map'] = 'Please provide a frame packet map. It cannot be empty.'
            self.input.status = 'failed'
            self.input.status_text = "Please provide a frame packet map. It cannot be empty.'"
            self._add_input_to_session(self.input)
            self.try_to_commit()
            return

        # TODO "new video" name makes less sense in new context
        new_video = New_video(
            session = self.session,
            project = self.project,
            input = self.input
        )

        try:
            new_video.update_from_frame_packet_map()
        except Exception as e:
            traceback.format_exc()
            self.input.update_log['error']['update_from_frame_packet_map'] = str(e)
            self.input.status = 'failed'
            self._add_input_to_session(self.input)
            logger.error(str(e))

        if len(self.input.update_log["error"].keys()) >= 1:
            self.input = self.update_video_status_when_update_has_errors(input = self.input)  # 'parent' here not frame
            self._add_input_to_session(self.input)

        # We should not declare success here, it's only started processing
        # TODO review if another state to put here like is_processing

    def update_video_status_when_update_has_errors(self, input):

        input.status = "failed"
        input.status_text = "See Update Log"
        input.update_log['last_updated'] = str(time.time())  # to make sure we trigger update
        return input

    def split_video_into_clips(self):
        """
        We expect video prepocess to handle clean up of clips it creates,
        the clean up at the end here is for the original full video file.

        We assume if this succeeds we return True

        It may return False, ie if the video is shorter
        then than the proposed split, in which case we just want to process
        it as a normal frame right?

        We assume if we return early ("not ok to split")
        there are no side effects, ie from doign the check.
        """
        global Video_Preprocess  # important

        try:
            video_preprocess = Video_Preprocess(
                session = self.session,
                parent_input = self.input
            )
        except Exception as exception:

            from methods.video.video_preprocess import Video_Preprocess

            video_preprocess = Video_Preprocess(
                session = self.session,
                parent_input = self.input
            )

        is_ok_to_split = video_preprocess.check_ok_to_split()

        if is_ok_to_split is False:
            return False

        video_preprocess.split_video()
        self.clean_up_temp_dir_on_thread()

        return True

    def create_task_on_job_sync_directories(self):
        """
            Given a file list, attach create tasks from those files attached to the given
            job.
        :param session:
        :param job:
        :param files:
        :return:
        """
        job_sync_manager = job_dir_sync_utils.JobDirectorySyncManager(
            session = self.session,
            job = self.input.job,
            log = self.log
        )
        return job_sync_manager.create_task_from_file(self.input.file)

    def update_jobs_with_attached_dirs(self):
        # From the file directory, get all related jobs.
        # TODO confirm how this works for pre processing case
        # Whitelist for allow types here, otherwise it opens a ton of connections while say processing frames
        if self.input.media_type not in ['image', 'video', 'sensor_fusion']:
            return

        directory = self.input.directory
        if directory is None:
            directory = self.project.directory_default
            logger.info(f"[update_jobs_with_attached_dirs] Default Dir Used : {self.project.directory_default}")

        jobs = JobWorkingDir.list(
            session = self.session,
            sync_type = 'sync',
            class_to_return = Job,
            working_dir_id = directory.id
        )
        for job in jobs:
            job_sync_dir_manger = job_dir_sync_utils.JobDirectorySyncManager(
                session = self.session,
                job = job,
                log = self.log
            )
            job_sync_dir_manger.create_file_links_for_attached_dirs(
                sync_only = True,
                create_tasks = True,
                file_to_link = self.input.file,
                file_to_link_dataset = self.working_dir,
                related_input = self.input,
                member = self.member
            )
            job.update_file_count_statistic(session = self.session)

            # Refresh the task stat count to the latest value.
            # We want to do this because there may be cases where 2 frames updated the task count
            # concurrently and that may lead to a bad end result of the counter.

            # Commit any update job/task data.
            self.try_to_commit()
            job.refresh_stat_count_tasks(self.session)

    def may_attach_to_job(self):

        if not self.input or not self.input.file:
            return

        if not self.input.job_id:
            return

        # We could use Job_permissions.check_job_after_project_already_valid()
        # But I'm not sure if raising in a thread is a good idea.
        Job_permissions.check_job_after_project_already_valid(
            job = self.input.job,
            project = self.project)

        result, log = WorkingDirFileLink.file_link_update(
            session = self.session,
            add_or_remove = "add",
            incoming_directory = self.input.directory,
            directory = self.input.job.directory,  # difference is this is from job
            file_id = self.input.file.id,
            job = self.input.job
        )

        # If job is not completed we should be creating tasks for the new files attached.
        if self.input.job.status in ['active', 'in_review']:
            self.create_task_on_job_sync_directories()

    def process_geo_tiff_file(self):
        geotiff_processor = GeoTiffProcessor(
            session = self.session,
            input = self.input,
            log = self.log
        )
        try:
            result, self.log = geotiff_processor.process_geotiff_data()

            if log_has_error(self.log):
                self.input.status = 'failed'
                logger.error(f"Geotiff file failed to process. Input {self.input.id}")
                logger.error(self.log)
                self.input.update_log = self.log
                return

            self.declare_success(self.input)

        except Exception as e:
            logger.error(f"Exception on process geo data: {traceback.format_exc()}")
            self.log['error']['geo_data'] = traceback.format_exc()
            self.input.status = 'failed'
            self.input.update_log = self.log

    def process_sensor_fusion_json(self):
        sf_processor = SensorFusionFileProcessor(
            session = self.session,
            input = self.input,
            log = self.log
        )

        try:
            result, self.log = sf_processor.process_sensor_fusion_file_contents()

            if log_has_error(self.log):
                self.input.status = 'failed'
                logger.error(f"Sensor fussion file failed to process. Input {self.input.id}")
                logger.error(self.log)
                self.input.update_log = self.log
                return

            self.declare_success(self.input)

        except Exception as e:
            logger.error(f"Exception on process sensor fusion: {traceback.format_exc()}")
            self.log['error']['process_sensor_fusion_json'] = traceback.format_exc()
            self.input.status = 'failed'
            self.input.update_log = self.log

    def check_free_tier_limits(self):
        if self.input.media_type not in ['image', 'text', 'sensor_fusion', 'video']:
            return

        directory = self.input.directory

        user_id = None
        user = None
        if self.input.member_created:
            user = self.input.member_created.user
            if user:
                user_id = user.id

        feature_checker = FeatureChecker(
            session = self.session,
            user = user,
            project = self.input.project
        )

        if self.input.media_type == 'video':
            max_file_count = feature_checker.get_limit_from_plan('MAX_VIDEOS_PER_DATASET')

        elif self.input.media_type == 'image':
            max_file_count = feature_checker.get_limit_from_plan('MAX_VIDEOS_PER_DATASET')

        elif self.input.media_type == 'text':
            max_file_count = feature_checker.get_limit_from_plan('MAX_TEXT_FILES_PER_DATASET')

        elif self.input.media_type == 'sensor_fusion':
            max_file_count = feature_checker.get_limit_from_plan('MAX_SENSOR_FUSION_FILES_PER_DATASET')
        else:
            return

        # Small optimization, avoid querying DB if no check is required (ie Premium Plans)
        if max_file_count is None:
            return

        file_count_dir = WorkingDirFileLink.file_list(
            session = self.session,
            working_dir_id = directory.id,
            limit = None,
            counts_only = True
        )

        logger.info('Free tier check for user: {} DIR[{}] File count: {}'.format(user_id,
                                                                                 directory.id,
                                                                                 file_count_dir))
        if max_file_count is not None and max_file_count <= file_count_dir:
            message = 'Free Tier Limit Reached - Max Files Allowed: {}. But Directory with ID: {} has {}'.format(
                max_file_count,
                directory.id,
                file_count_dir)
            logger.error(message)
            self.log['error']['free_tier_limit'] = message
            self.log['info']['feature_checker'] = feature_checker.log
            self.input.status = 'failed'
            self.input.description = message
            self.input.update_log = self.log
            return False

    def route_based_on_media_type(self):
        """

        Route to function based on self.input.media_type

        """
        strategy_operations = {
            "image": self.process_one_image_file,
            "text": self.process_one_text_file,
            "audio": self.process_one_audio_file,
            "frame": self.process_frame,
            "sensor_fusion": self.process_sensor_fusion_json,
            "geo_tiff": self.process_geo_tiff_file,
            "video": self.process_video,
            "csv": self.process_csv_file
        }

        operation = None

        if not self.input:
            self.log['error']['input class'] = "No valid Input class"
            return

        if self.input:
            # Do we need self.input check here? aren't we checking if it's None already

            operation = strategy_operations.get(self.input.media_type, None)

        if operation is None:
            self.log['error']['media_type'] = "Invalid kind (No operation matches.)"
            return

        operation()

    def check_limits(self):

        # Limits for uploading
        # Cache's check and only re runs every x seconds
        if self.working_dir.file_limit_time is None or \
            time.time() > self.working_dir.file_limit_time + 7200:

            print("[process media] Checking limits")

            directory_file_count = WorkingDirFileLink.file_list(
                session = self.session,
                working_dir_id = self.working_dir_id,
                type = "image",
                counts_only = True,
                limit = None)
            # Could also try to cache this as files get added...

            # Reject
            if directory_file_count >= self.directory_file_count_limit:
                self.input.status = "failed"
                self.input.status_text = "Reached a per directory limit." + \
                                         "Please contact us to increase limit."
                return False
            # Accept and update cache
            else:
                self.session.add(self.working_dir)
                self.working_dir.file_limit_time = time.time()

        return True

    def try_to_commit(self):
        """
        We don't commit the frame type because we are
        just using the object to store the same concepts
        and data, but otherwise do NOT want to persist it.
        TODO thoughts about making this concept more generic,
        and/or part of some logging thing...
        """

        if self.input and self.input.media_type == "frame":
            return

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def read_raw_file(self):
        # Get Raw file
        # TODO not fan that this defaults to in the negative
        # We guarantee this to be False by default from item default and init
        if self.file_is_numpy_array is False:
            with open(self.input.temp_dir_path_and_filename, "rb") as raw_file:

                try:
                    self.raw_numpy_image = imread(raw_file)
                except:
                    self.input.status = "failed"
                    self.input.status_text = "Could not open file"
                    return False

    def read_raw_text_file(self):
        # Get Raw file
        self.raw_text_file = open(self.input.temp_dir_path_and_filename, "rb")
        print(self.raw_text_file)
        return self.raw_text_file

    def process_frame(self):
        """
        We don't create a file as we rely on Annotation_Update()
        to create that if needed

        We don't create an image, as we save the data to the video dict.
        In general this is not for previewing an image from front end
        but more for "internal" access.
        if needed could cache WORsigned urls on front end

        We don't call resize because we assume the video has already been
        resized as required

        I still like of using input to track this because it can track
        retries, progress, other success stuff etc...

        We use the video id, because even if the parent thing changes
        the raw data stays the same right?

        As long as we store the "root" blob path, then we know
        the frame number is only extra thing on top of it right?
        And thumb is + "_thumb"?

        We store the blob path on the video so if we want to change it we can
        otherwise assumption is it's just the frame number
        + _thumb


        Jan 10, 2020, Only thumbnails for first frame because:
         1) No clear usage for other thumbnails yet
         2) We can regenerate the thumbnails on demand later if needed
         3) Primary issue is loading time, and this appears to shave off 50%
         of frame processing time (which is 25->40% of overall time.)

        """
        print(f"Processing Frame: {self.frame_number}")
        try:
            result = self.read_raw_file()
            if result is False: return False

            self.process_image_for_frame()

            if self.frame_number == 0:
                self.process_thumbnail_image_for_frame()
        except Exception as e:
            log = regular_log.default()
            log['error'] = traceback.format_exc()

            self.proprogate_frame_instance_update_errors_to_parent(log)

            logger.error(f"Error Processing frame {self.frame_number}, input {self.input.id} ")
            logger.error(traceback.format_exc())

    def process_image_for_frame(self):

        self.blob_path_to_frame = self.input.root_blob_path_to_frames + str(self.frame_number)

        self.save_and_upload(path = self.blob_path_to_frame)

        self.process_first_frame_of_video()

        self.video_status_updates()

    def process_thumbnail_image_for_frame(self):

        self.raw_numpy_image = imresize(self.raw_numpy_image, (160, 160))

        # assumed to be called after path is built?
        # I don't think this is quite the right name yet
        self.blob_path_to_frame += "_thumb"

        self.save_and_upload(path = self.blob_path_to_frame)

    def save_and_upload(self, path):
        # Trying to make this a bit more generic could maybe use with
        # process_image too

        temp_local_path = self.input.temp_dir + "/resized_" + str(time.time()) + \
                          str(self.input.extension)

        imwrite(temp_local_path, self.raw_numpy_image)

        data_tools.upload_to_cloud_storage(
            temp_local_path = temp_local_path,
            blob_path = path,
            content_type = "image/jpg"
        )

    def process_first_frame_of_video(self):

        # April 7, 2020, prior this had more functions, now
        # Done in different places, still may be useful in future
        return

        if self.video_id and self.frame_number == 0:
            video = self.session.query(Video).filter(
                Video.id == self.video_id).one()
            # we don't save a preview image here anymore since we can
            # generate it on demand as needed...
            # but we could call
            # self.preview_image_url_thumb = self.get_frame_url(
            #			frame_number = 0, thumb=True)
            # if we wanted to cache it?

            self.session.add(video)

    def video_status_updates(self):
        """
        This status is more important then it may at first appear because
        * We condition retry on it
        * Condition job launch on it
        * May be other things in future given 2 already

        Feb 12, 2020
            Realized suspect that without the lock (on both), if it happens
            to update the video to pushing frames after it's complete
            that can cause issues. Context that we now process on say
            8 different threads / frames running in parallel

            I wonder if it would be better pro actively flag this
            ie flag it when we insert it.

            Also could build in a retry here, so that the
            last one retries a number of times to mark it complete...
            (ie if by chance another thread had the other status update
            and the state estimate was off...)...

            Started trying to refactor this into it's own thing.

            TODO not super happy with this whole sorta setup with
            # parent_input code duplication here
            # The rationale is that we only want to fire this request when needed
            # perhaps these could be separate functions are something?

            I think we may need to abstract the conditional statement
            so that we only run that once...

            Main leave off is not sure if super happy with how aggressive
            get_parent_input_with_retry() is,
            Is there a way we can pass a paremeter to the retry thing?
            ie want it to be very aggressive (at getting thing)
            for final one but less so for status updates.

        Jan 23, 2020
            The magic number for this is a little tough
            In large jobs, most of this updating is not needed
            However we do need to update every so often to keep
            retry system happy
            and for smaller jobs, too large of a number may
            result in bad UI experience. perhaps this should
            scale on some factor of video length.


        Why the +2?
        It's possible the frame number could be slightly off from the video parent length.
        """
        if not self.input.video_parent_length:
            return

        if self.input.mode == 'copy_file' and self.num_frames_to_update != 0 and self.frame_completion_controller is not None:
            # For video copy update every 10th part the amount of total frames
            run_every_x_number_of_frames = int(round(self.num_frames_to_update / 10))
            run_every_x_number_of_frames = max(1, run_every_x_number_of_frames)
            # If we're at least 20 frames before the last one. It means we're near the last frame.
            near_last_frame: bool = (
                                        self.frame_completion_controller.get_total_frames() - self.frame_completion_controller.completed_frames) <= 5
            # Count the completed frame to track progress.
            time_to_update_frame: bool = self.frame_completion_controller.completed_frames % run_every_x_number_of_frames == 0
        else:
            # Default to 60 frames for video uploads
            run_every_x_number_of_frames = 60

            # We use these conditions twice
            # upfront to save hitting DB, then after to route which way to go.
            near_last_frame: bool = self.frame_number + 2 >= self.input.video_parent_length
            time_to_update_frame: bool = self.frame_number % run_every_x_number_of_frames == 0

        if near_last_frame is True or time_to_update_frame is True:

            parent_input = self.get_parent_input_with_retry()
            if parent_input:
                if near_last_frame is True:
                    self.declare_success(input = parent_input)
                    if self.input.mode == 'copy_file' and time_to_update_frame:
                        estimated_percent_complete = (
                                                         self.frame_completion_controller.completed_frames / self.num_frames_to_update) * 100

                elif time_to_update_frame is True:
                    if self.input.mode == 'copy_file':
                        estimated_percent_complete = (
                                                         self.frame_completion_controller.completed_frames / self.num_frames_to_update) * 100
                    else:
                        # File upload case:  Context that this is only x percent (ie 20) of the overall processing.
                        new_work_done_estimate = (run_every_x_number_of_frames / self.input.video_parent_length) * 20
                        estimated_percent_complete = parent_input.percent_complete + new_work_done_estimate

                    if estimated_percent_complete >= 100:
                        self.declare_success(input = parent_input)
                    else:
                        parent_input.status = "processing_frames_in_queue"
                        parent_input.percent_complete = estimated_percent_complete

                self._add_input_to_session(parent_input)

        """
        We only want to run this once. But the parent input thing could fire multiple times
        And we don't want to wait for skip lock - each of these sequences should be unique 
        so waiting with retry would confuse it.
        """
        if self.frame_number + 2 == self.input.video_parent_length:
            if self.input.parent_file_id and self.input.video_was_split is None:
                print("Running sequence update")
                time.sleep(2)  # just give a little breather while stuff is settling.
                self.update_sequences()

    @retry(wait = wait_random_exponential(multiplier = 2, max = 20),
           stop = stop_after_attempt(5))
    def get_parent_input_with_retry(self):
        """
        """
        print("ran get_parent_input_with_retry")

        parent_input = Input.get_by_id(
            session = self.session,
            id = self.input.parent_input_id,
            skip_locked = True)
        if parent_input is None:
            raise Exception

        return parent_input

    def declare_success(
        self,
        input: Input):
        """
        Caution, for video we are assuming this is the "parent_input"
        we bounce between self.input and input

        It's possible for this to be called multiple times?
        So if it's already success just return
        """

        if input.status == "success":
            return
        if input.file_id is None and input.file is not None:
            input.file_id = input.file.id

        logger.debug(f'Success Processing Input: {input.id} {input.mode} - {input.type}')
        Event.new_deferred(
            session = self.session,
            kind = 'input_file_uploaded',
            project_id = input.project_id,
            directory_id = input.directory_id,
            input_id = input.id,
            file_id = input.file_id,
            wait_for_commit = True
        )
        input.percent_complete = 100
        input.status = "success"
        input.time_completed = datetime.datetime.utcnow()

        if input.batch_id is not None:
            input.batch.check_for_completion_and_complete(self.session)

        return input

    def update_sequences(self):
        """
        Because we run the annotation updates in parallel
        it seems cleaner to do an "after" update thing to sequences

        an alternative is we could pro-actively add the keyframe
        list when it's first created. But this way we use an
        "existing" method.
            Also in the future if we expand this to do some other type of update
            /work could be useful to run "after".

        """
        Sequence.update_all_sequences_in_file(
            session = self.session,
            video_file_id = self.input.parent_file_id,
            regenerate_preview_images = True)

    def process_one_audio_file(self):
        try:
            logger.debug(f"Started processing audio file from input: {self.input_id}")

            self.new_audio_file = AudioFile(original_filename = self.input.original_filename)
            self.session.add(self.new_audio_file)
            self.session.flush()

            self.try_to_commit()

            if self.project:
                # with either object or id... this assumes we don't have project_id set.
                self.project_id = self.project.id

            ### Main
            self.save_raw_audio_file()

            self.input.file = File.new(
                session = self.session,
                working_dir_id = self.working_dir_id,
                file_type = "audio",
                audio_file_id = self.new_audio_file.id,
                original_filename = self.input.original_filename,
                project_id = self.project_id,
                input_id = self.input.id,
                file_metadata = self.input.file_metadata,
            )

            if self.input.status != "failed":
                self.input.status = "success"
                self.input.percent_complete = 100
                self.input.time_completed = datetime.datetime.utcnow()

            try:
                shutil.rmtree(self.input.temp_dir)  # delete directory
            except OSError as exc:
                logger.error("shutil error")
                pass
        except Exception as e:
            message = traceback.format_exc()
            logger.error(message)
            self.log['error']['text_file_upload'] = message
            self.input.status = 'failed'
            self.input.description = message
            self.input.update_log = self.log

        return True

    def process_one_text_file(self):
        """
            This function will process a single text file and Create a Row in Table
            TextFile()
        """
        try:
            logger.debug(f"Started processing text file from input: {self.input_id}")
            result = self.read_raw_text_file()
            if not result:
                logger.error(f"Error reading text file {self.input.temp_dir_path_and_filename}")
            # Why is content_type needed here?
            # self.content_type = "image/" + str(self.input.extension)

            # Image() subclass
            self.new_text_file = TextFile(original_filename = self.input.original_filename)
            self.session.add(self.new_text_file)
            self.session.flush()

            self.try_to_commit()

            if self.project:
                # with either object or id... this assumes we don't have project_id set.
                self.project_id = self.project.id

            ### Main
            self.save_raw_text_file()

            self.input.file = File.new(
                session = self.session,
                working_dir_id = self.working_dir_id,
                file_type = "text",
                text_file_id = self.new_text_file.id,
                original_filename = self.input.original_filename,
                project_id = self.project_id,
                input_id = self.input.id,
                file_metadata = self.input.file_metadata,
                text_tokenizer = 'nltk'
            )
            raw_text = result.read()
            raw_text = raw_text.decode('utf-8')
            self.save_text_tokens(raw_text, self.input.file)
            # Set success state for input.
            if self.input.media_type == 'text':
                if self.input.status != "failed":
                    self.declare_success(self.input)
                try:
                    shutil.rmtree(self.input.temp_dir)  # delete directory
                except OSError as exc:
                    logger.error("shutil error")
                    pass
        except Exception as e:
            message = traceback.format_exc()
            logger.error(message)
            self.log['error']['text_file_upload'] = message
            self.input.status = 'failed'
            self.input.description = message
            self.input.update_log = self.log

        return True

    def rotate_instance_list(self, instance_list, width, height):

        if not instance_list:
            return
        logger.warning('Rotating Instance List')
        for i in range(0, len(instance_list)):
            instance_list[i] = rotate_instance_dict_90_degrees(instance = instance_list[i],
                                                               width = width,
                                                               height = height)

        return instance_list

    def check_metadata_and_auto_correct_instances(self, imageio_read_image, image_metadata):
        if not self.input.auto_correct_instances_from_image_metadata:
            return
        if not image_metadata:
            return
        if image_metadata.get('width') is None or image_metadata.get('height') is None:
            return
        logger.info('Checking matching metadata and readed image width/height...')
        readed_image_height = imageio_read_image.shape[0]
        readed_image_width = imageio_read_image.shape[1]
        logger.info(f'Readed Image width: {readed_image_width} height: {readed_image_height}')

        if readed_image_width == readed_image_height:
            return

        metadata_width = image_metadata.get('width')
        metadata_height = image_metadata.get('height')
        logger.info(f'Metadata width: {metadata_width} height: {metadata_height}')

        if metadata_height == readed_image_width and metadata_width == readed_image_height:
            logger.warning('Detected flipped coordinates on image. Rotating instances to correct positioning')
            if self.input.instance_list and self.input.instance_list.get('list'):
                self.input.instance_list['list'] = self.rotate_instance_list(self.input.instance_list.get('list'),
                                                                             readed_image_width,
                                                                             readed_image_height)

    def save_image_and_thumbnails(self):
        self.resize_raw_image()

        self.check_metadata_and_auto_correct_instances(
            imageio_read_image = self.raw_numpy_image,
            image_metadata = self.input.image_metadata
        )

        self.save_raw_image_file()
        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error save_raw_image_file")
            return
        self.save_raw_image_thumb()
        if len(self.log["error"].keys()) >= 1:
            logger.error(f"Error save_raw_image_thumb")
            return

    def determine_image_upload_strategy(self) -> str:
        """
            Determines the upload strategy based on available upload data.
        :return:
        """
        if self.input.type == "from_blob_path" \
            and self.input.bucket_name is not None \
            and self.input.raw_data_blob_path is not None:
            return "connection_processing"
        else:
            return "standard_processing"

    def create_image_object_from_input(self):
        self.new_image = Image(original_filename = self.input.original_filename)

        self.session.add(self.new_image)
        self.session.flush()

        return self.new_image

    def create_image_file_from_input(self):
        self.input.file = File.new(
            session = self.session,
            working_dir_id = self.working_dir_id,
            file_type = "image",
            image_id = self.new_image.id,
            original_filename = self.input.original_filename,
            project_id = self.project_id,  # TODO test if project_id is working as expected here
            input_id = self.input.id,
            connection_id = self.input.connection_id,
            bucket_name = self.input.bucket_name,
            file_metadata = self.input.file_metadata,

        )
        return self.input.file

    def connection_image_processing(self):

        self.new_image = self.create_image_object_from_input()
        # Set URL
        self.new_image.url_signed_blob_path = self.input.raw_data_blob_path
        self.try_to_commit()

        if log_has_error(self.log):
            self.input.status = 'failed'
            logger.error(f"failed to process connection upload. Log: {self.log}")
            logger.error(self.log)
            self.input.update_log = self.log

        self.input.file = self.create_image_file_from_input()

        self.populate_new_models_and_runs()

        if log_has_error(self.log):
            self.input.status = 'failed'
            logger.error(f"failed to generation URL. Log: {self.log}")
            logger.error(self.log)
            self.input.update_log = self.log
        # Handle status checks
        if self.input.media_type == 'image':
            if self.input.status != "failed":  # if we haven't already set a status
                self.declare_success(self.input)

    def standard_image_processing(self):
        # Read file if it does not come from a blob
        result = self.read_raw_file()
        if result is False:
            return False

        self.new_image.url_signed_blob_path = settings.PROJECT_IMAGES_BASE_DIR + \
                                              str(self.project_id) + "/" + str(self.new_image.id)

        self.try_to_commit()

        # Save thumbnails if we are uploading blobs, otherwise skip
        self.save_image_and_thumbnails()
        if log_has_error(self.log):
            return

        self.input.file = self.create_image_file_from_input()

        self.populate_new_models_and_runs()

        # Handle status checks
        if self.input.media_type == 'image':

            if self.input.status != "failed":  # if we haven't already set a status
                self.declare_success(self.input)

            if self.input.type != 'from_blob_path':
                try:
                    shutil.rmtree(self.input.temp_dir)  # delete directory
                except OSError as exc:
                    print("shutil error")
                    pass

    def process_one_image_file(self):
        """
            Adds an image file into diffgram from self.input data.
        :return:
        """
        try:
            self.new_image = self.create_image_object_from_input()
            if self.project:
                self.project_id = self.project.id

            strategy = self.determine_image_upload_strategy()
            if strategy == "connection_processing":
                self.connection_image_processing()
            else:
                self.standard_image_processing()

            # Refresh Previews of project
            self.project.set_cache_key_dirty('preview_file_list')
            return True
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(f'Error on process_one_image_file {msg}')
            self.input.status = 'failed'
            self.log['error']['process_one_image'] = str(e)
            self.log['error']['trace'] = msg
            self.input.update_log = self.log
            return False

    def __get_allowed_model_ids(self):
        models = Model.list(session = self.session, project_id = self.project_id)
        return [m.id for m in models]

    def __get_allowed_model_run_ids(self):
        model_run_list = ModelRun.list(session = self.session, project_id = self.project_id)
        return [m.id for m in model_run_list]

    def process_existing_instance_list(self, init_existing_instances = False):
        """
        Assumptions
            For both video and images, this is only if the instance list
            exists. So the default is for it to be empty.


        While we have self.input.media_type available
        we do simliar end goal for both

        Curious if better way to test this individual function here
        """
        if not self.input.instance_list:
            return

        if self.input.media_type not in ['image', 'frame', 'text']:
            return
        # caution, due to workaround have to get 'list' key from dict
        # instance_list on Input class is actually a 'dict' with key 'list'.

        instance_list = self.input.instance_list.get('list')
        task = None
        should_complete_task = False
        if not instance_list:
            return

        file = None
        if self.input.media_type in ['image', 'text']:
            file_id = self.input.file.id
            file = self.input.file
            video_data = None

            if self.input.task_id:
                task = Task.get_by_id(self.session, task_id = self.input.task_id)

            # We just complete it for images and text, 
            # video files are handled by __update_parent_video_at_last_frame()
            should_complete_task = self.input.task_action == 'complete_task'

        elif self.input.media_type == 'frame':
            file_id = self.input.parent_file_id
            file = File.get_by_id(self.session, file_id)

            video_data = {
                'video_mode': True,
                'video_file_id': file_id,
                'current_frame': self.frame_number  # TODO Consider this from input for better consistency
            }

        else:
            logger.error(f"Invalid media type {self.input.media_type}")
            return

        allowed_model_id_list = self.__get_allowed_model_ids()
        allowed_model_runs_id_list = self.__get_allowed_model_run_ids()
        try:
            annotation_update = Annotation_Update(
                session = self.session,
                file = file,
                instance_list_new = instance_list,
                project_id = self.input.project_id,
                video_data = video_data,
                task = task,
                complete_task = should_complete_task,
                member = self.member,
                do_init_existing_instances = init_existing_instances,
                external_map = self.input.external_map,
                external_map_action = self.input.external_map_action,
                do_update_sequences = False,
                allowed_model_id_list = allowed_model_id_list,
                allowed_model_run_id_list = allowed_model_runs_id_list,
                force_lock = False
            )
            # This returns original file type which would be different
            new_file = annotation_update.main()
            # Because we don't have great way to handle old and new yet
            # Maybe just do this for update mode
            # Careful, for frames, "file" changes here.
            # eg file doesn't exist, then annotation creates it.
            annotation_update.file.set_cache_key_dirty('instance_list')

            # Propgate errors if any back up to input
            if len(annotation_update.log["error"].keys()) >= 1:
                self.input.status = "failed"
                self.input.status_text = "Instance List Error:" + \
                                         str(annotation_update.log["error"]) + \
                                         " On SDK?: Some types of errors may be resolved by updating to latest."

                if self.input.media_type == 'frame':
                    # Note at the moment we don't propagate info that's not an error
                    # to save computation? hmmmm
                    self.proprogate_frame_instance_update_errors_to_parent(
                        error_log = annotation_update.log["error"])

                return False
            return True

        except Exception as e:
            trace = traceback.format_exc()
            self.input.status = "failed"
            self.input.status_text = f"Instance List Creation error: {trace}"
            logger.error(trace)

            return False

    def proprogate_frame_instance_update_errors_to_parent(self,
                                                          error_log: dict):
        """
         
        """
        parent_input = self.get_parent_input_with_retry()
        parent_input.status = "failed"
        parent_input.status_text = "See Update Log"
        if not parent_input.update_log:
            parent_input.update_log = regular_log.default()

        parent_input.update_log['error'][f"Frame {str(self.frame_number)}"] = error_log
        parent_input.update_log['last_updated'] = str(time.time())

        self._add_input_to_session(parent_input)

    def save_raw_image_file(self):

        # Use original file for jpg and jpeg
        extension = str(self.input.extension).lower()
        if extension in ['.jpg', '.jpeg']:
            new_temp_filename = self.input.temp_dir_path_and_filename
        # If PNG is used check compression
        elif extension == '.png':
            new_temp_filename = self.input.temp_dir_path_and_filename
            with open(self.input.temp_dir_path_and_filename, 'rb') as f:
                f.seek(63)
                read_value = f.read(1)
                compress = (read_value == b'\x01')

            # If compress_level 0 or 1 write file with compress_level=2 and point to new file instead
            if (compress):
                new_temp_filename = self.input.temp_dir + "/resized_" + str(time.time()) + \
                                    str(self.input.extension)
                imwrite(new_temp_filename, np.asarray(self.raw_numpy_image), compress_level = 2)
        # For bmp, tif and tiff files save as PNG and compress
        elif extension in ['.bmp', '.tif', '.tiff']:
            new_temp_filename = f"{self.input.temp_dir}/resized_{str(time.time())}.png"
            imwrite(new_temp_filename, np.asarray(self.raw_numpy_image), compress_level = 3)
        else:
            self.input.status = "failed"
            self.input.status_text = f"""Extension: {self.input.extension} not supported yet. 
                Try adding an accepted extension [.jpg, .jpeg, .png, .bmp, .tif, .tiff] or no extension at all if from cloud source and response header content-type is set correctly."""
            self.log['error']['extension'] = self.input.status_text
            return

        try:
            data_tools.upload_to_cloud_storage(
                temp_local_path = new_temp_filename,
                blob_path = self.new_image.url_signed_blob_path,
                content_type = "image/jpg",
            )

        except Exception as e:
            message = f'Error uploading to cloud storage: {traceback.format_exc()}'
            logger.error(message)
            self.input.status = 'failed'
            self.log['error']['upload_image'] = message
            self.input.update_log = self.log
            return

        return new_temp_filename

    def save_text_tokens(self, raw_text: str, file: File) -> None:
        # By Default, file has NLTK tokenizer.
        tokenizer = TextTokenizer(type = file.text_tokenizer)

        word_tokens = tokenizer.tokenize_words(raw_text)
        sentences_tokens = tokenizer.tokenize_sentences(raw_text)

        json_data = {
            file.text_tokenizer: {
                'words': word_tokens,
                'sentences': sentences_tokens
            }
        }
        json_string_data = json.dumps(json_data)
        self.new_text_file.tokens_url_signed_blob_path = '{}{}/{}_tokens.json'.format(
            settings.PROJECT_TEXT_FILES_BASE_DIR,
            str(self.project_id),
            str(self.new_text_file.id))
        logger.debug(f'Blob path Tokens: {self.new_text_file.tokens_url_signed_blob_path}')
        data_tools.upload_from_string(self.new_text_file.tokens_url_signed_blob_path,
                                      json_string_data,
                                      content_type = 'application/json')
        self.new_text_file.tokens_url_signed = data_tools.build_secure_url(
            self.new_text_file.tokens_url_signed_blob_path,
            self.new_text_file.tokens_url_signed_expiry)
        logger.info(f"Saved Tokens on: {self.new_text_file.tokens_url_signed_blob_path}")

    def save_raw_audio_file(self):
        offset = 2592000
        self.new_audio_file.url_signed_expiry = int(time.time() + offset)  # 1 month

        self.new_audio_file.url_signed_blob_path = '{}{}/{}'.format(settings.PROJECT_TEXT_FILES_BASE_DIR,
                                                                    str(self.project_id),
                                                                    str(self.new_audio_file.id))

        # TODO: Please review. On image there's a temp directory for resizing. But I don't feel the need for that here.
        logger.debug(f"Uploading text file from {self.input.temp_dir_path_and_filename}")

        data_tools.upload_to_cloud_storage(
            temp_local_path = self.input.temp_dir_path_and_filename,
            blob_path = self.new_audio_file.url_signed_blob_path,
            content_type = "text/plain",
        )

        self.new_audio_file.url_signed = data_tools.build_secure_url(self.new_audio_file.url_signed_blob_path,
                                                                     offset)

    def save_raw_text_file(self):
        offset = 2592000
        self.new_text_file.url_signed_expiry = int(time.time() + offset)  # 1 month

        self.new_text_file.url_signed_blob_path = '{}{}/{}'.format(settings.PROJECT_TEXT_FILES_BASE_DIR,
                                                                   str(self.project_id),
                                                                   str(self.new_text_file.id))

        # TODO: Please review. On image there's a temp directory for resizing. But I don't feel the need for that here.
        logger.debug(f"Uploading text file from {self.input.temp_dir_path_and_filename}")

        data_tools.upload_to_cloud_storage(
            temp_local_path = self.input.temp_dir_path_and_filename,
            blob_path = self.new_text_file.url_signed_blob_path,
            content_type = "text/plain",
        )

        self.new_text_file.url_signed = data_tools.build_secure_url(self.new_text_file.url_signed_blob_path,
                                                                    offset)

        # Now Save Tokens

    def save_raw_image_thumb(self):
        """
        Would be nice to share this with original file save
        but follows different process sorta
        """

        # Save Thumb
        self.new_image.url_signed_thumb_blob_path = f"{self.new_image.url_signed_blob_path}_thumb"

        thumbnail_image = imresize(self.raw_numpy_image, (160, 160))

        new_temp_filename = f"{self.input.temp_dir}/resized.jpg"

        imwrite(new_temp_filename, thumbnail_image, quality = 95)

        data_tools.upload_to_cloud_storage(
            temp_local_path = new_temp_filename,
            blob_path = self.new_image.url_signed_thumb_blob_path,
            content_type = "image/jpg",
        )

    def get_and_set_width_and_height(
        self,
        diffgram_image,
        imageio_read_image):

        diffgram_image.height = imageio_read_image.shape[0]
        diffgram_image.width = imageio_read_image.shape[1]

    def resize_raw_image(self):

        if len(self.raw_numpy_image.shape) == 3:
            channels = self.raw_numpy_image.shape[2]
            if channels == 4:
                # Careful, if black and white this will fail (hence only running if 4 channels)
                self.raw_numpy_image = self.raw_numpy_image[:, :, :3]  # remove alpha channel

        if self.raw_numpy_image is None:
            raise IOError("Could not open")

        self.get_and_set_width_and_height(
            diffgram_image = self.new_image,
            imageio_read_image = self.raw_numpy_image)

        max_size = settings.DEFAULT_MAX_SIZE

        if self.new_image.height > max_size or self.new_image.width > max_size:
            ratio = min((max_size / self.new_image.height),
                        (max_size / self.new_image.width))

            shape_x = int(round(self.new_image.width * ratio))
            shape_y = int(round(self.new_image.height * ratio))

            self.raw_numpy_image = imresize(self.raw_numpy_image,
                                            (shape_x, shape_y))

            self.get_and_set_width_and_height(
                diffgram_image = self.new_image,
                imageio_read_image = self.raw_numpy_image)

    def process_csv_file(self):
        """
        Purpose:
            Handle complete file input, including processing indvidiaul rows

        Arguments:
            session, object
            input, CSV file input
            temp_dir_path_and_filename, String

        Returns:
            True if completed

        """

        row_limit = 10000
        with open(self.input.temp_dir_path_and_filename) as csv_file:

            csv_reader = csv.reader(csv_file)

            for index, row in enumerate(csv_reader):

                if index >= row_limit:
                    print("Reached row limit")
                    break

                # TODO handle if row[0] is empty if that's possible

                row_input = Input()
                self.session.add(row_input)

                row_input.temp_dir = tempfile.mkdtemp()
                row_input.directory_id = self.input.directory_id
                row_input.project = self.project
                row_input.member = self.member
                row_input.url = row[0]
                row_input.allow_csv = False
                row_input.type = "from_url"
                row_input.media_type = None
                self.try_to_commit()

                # Spawn a new instance for each url
                # To keep orginal instance seperate

                item = PrioritizedItem(
                    priority = 100,
                    input_id = row_input.id)
                add_item_to_queue(item)

        # TODO how to handle removing from directory
        # When we end up adding process media things to a queue instead
        # of just firing them

        # We did not remove the temporary directory
        # while looping so do it now
        # try:
        #	shutil.rmtree(self.input.temp_dir)
        # except OSError as exc:
        #	pass

        # TODO, the last successful item should set this...
        self.input.status = "success"
        return True

    def download_media(self):
        """
        errors stored in self.log['error'] for easier
        passing back through to other parts of system
        """

        # Special case... ?
        if self.input.type == "from_url" and self.input.url is None:
            self.input.status = "failed"
            self.input.status_text = "Invalid url (None provided)"
            self.log['error']['status_text'] = self.input.status_text
            return

        """
        Not clear if we need more shopisticated conditioning here
        ie should we default to downloading it again? or default
        to our path? When we are retrying is this something to condition
        on?
        """
        try:
            # In our storage already
            if self.input.raw_data_blob_path:
                self.download_from_cloud_storage_to_file()

            elif self.input.url:
                self.download_from_url()
        except Exception as e:
            trace_data = traceback.format_exc()
            logger.error('Error downloading media')
            logger.error(trace_data)
            self.log['download_media'] = str(e)
            self.log['trace'] = trace_data
            self.input.status = "failed"
            self.input.status_text = "Error downloading media."

        logger.info(f"{str(self.input.id)} InputID Probably Downloaded")

    def download_from_cloud_storage_to_file(self):

        # TODO would prefer this part to be in data tools...

        self.input.temp_dir = tempfile.mkdtemp()

        self.input.temp_dir_path_and_filename = self.input.temp_dir + "/" + \
                                                str(time.time()) + str(self.input.extension)

        with open(self.input.temp_dir_path_and_filename, 'wb') as file_obj:

            try:

                data_tools.download_from_cloud_to_local_file(
                    cloud_uri = self.input.raw_data_blob_path,
                    local_file = file_obj
                )
            except Exception as e:
                self.log['error']['status_text'] = "{} download_from_cloud_to_local_file exception {}".format(
                    settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
                    str(e)
                )
                self.input.status = "failed"
                self.input.status_text = self.log['error']['status_text']
                self.input.update_log = self.log
                return

        self.input.status = "downloaded"

    def download_from_url(self):
        # https://diffgram.com/docs/download_from_url-process-media
        if self.input.url[0: 4] != "http":
            self.input.status = "failed"
            self.input.status_text = "Invalid url (Did not start with http)"
            self.log['error']['status_text'] = self.input.status_text

            logger.error(f"Exceeded retry limit, no valid response LOG: {str(self.log)}")
            return
        self.input.original_filename, self.input.extension = get_file_name_and_extension(
            self.input.url, input_original_filename = self.input.original_filename)
        if self.input.extension is None:
            self.input.status = "failed"
            self.input.status_text = "Invalid extension, check filename"
            self.log['error']['status_text'] = self.input.status_text
            return
        # Add extension to name: ffmpeg requires the filename with the extension.
        # check the split() function in video_preprocess.py
        if self.input.original_filename and not self.input.original_filename.endswith(self.input.extension):
            self.input.original_filename = self.input.original_filename + self.input.extension

        if self.__file_does_not_exist_in_target_directory() is False:
            self.log['error']['status_text'] = self.input.status_text
            return

        split_url = urlsplit(self.input.url)
        response = requests.get(self.input.url, stream = True)

        if response.status_code != 200:
            self.input.status = "failed"
            logger.error(
                "Exceeded retry limit, no valid response ({}) from {} Response: {}".format(response.status_code,
                                                                                           self.input.url,
                                                                                           str(response.text)))
            self.input.status_text = "Exceeded retry limit, no valid response ({}) from {} Response: {}".format(
                response.status_code, self.input.url, str(response.text))
            self.log['error']['status_text'] = self.input.status_text
            return

        if response.status_code == 200:
            # extension-detection https://diffgram.com/docs/download_from_url-process-media#extension-detection
            # Handling of 'application/octet-stream'  https://diffgram.com/docs/download_from_url-process-media#handling-of-applicationoctet-stream

            if self.input.extension is None:

                content_type = response.headers.get('content-type', None)

                if not content_type:

                    self.input.status = "failed"
                    self.input.status_text = "Invalid Extension. No 'content-type' provided."
                    self.log['error']['status_text'] = self.input.status_text
                    return

                else:
                    # Careful this is untrusted
                    trial_extension = content_type.split("/")
                    # This feels verbose, but is to try and more gracefully handle different content types
                    # Since we are checking length anyway it seems natural to accept the next one
                    # Perhaps there is some other way we can avoid this? Or at least push it into determine media
                    # type or something...
                    if len(trial_extension) == 2:
                        # Assume it's the second one
                        self.input.extension = f".{trial_extension[1]}"
                    elif len(trial_extension) == 1:
                        # handle if only one item (ie "video" not "video/extension") Is there a better way to
                        # test for this?
                        self.input.extension = f".{trial_extension[0]}"
                    else:
                        # Unexpected case, not default "/" split, and not a single extension.
                        self.input.status = "failed"
                        self.input.status_text = f"Invalid Extension{str(content_type)}"
                        self.log['error']['status_text'] = self.input.status_text
                        return

            if self.input.media_type is None:
                self.input.media_type = self.determine_media_type(
                    extension = self.input.extension,
                    allow_csv = self.allow_csv)

            if self.input.media_type is None or \
                self.input.media_type not in ["image", "video"]:
                self.input.status = "failed"
                self.input.status_text = f"Invalid media type: {str(self.input.extension)}"
                self.log['error']['status_text'] = self.input.status_text
                return

            self.input.temp_dir = tempfile.mkdtemp()

            self.input.temp_dir_path_and_filename = self.input.temp_dir + "/" + \
                                                    str(time.time()) + str(self.input.extension)

            # Note this uses a lot of memory if the item is large
            # We could explore http://requests.kennethreitz.org/en/master/api/#requests.Response.iter_content
            # If this is needed
            try:
                with open(self.input.temp_dir_path_and_filename, 'wb') as f:
                    f.write(response.content)
                logger.info(f"{str(self.input.id)} ID Write Finished")
            except:
                logger.info(f"{str(self.input.id)} ID Failure to write")

            self.input.status = "downloaded"

    def _add_input_to_session(self, input):
        """
            This helper function prevents adding frame inputs to the session
            since the convention is that frames always stay in memory and should
            be never commmited or added to an sql alchemy session.
        :param input:
        :return:
        """
        if input.media_type == 'frame':
            return

        self.session.add(input)

    def populate_new_models_and_runs(self):
        if self.input.media_type == 'video':
            if not self.input.frame_packet_map:
                return
            frame_packet_map = self.input.frame_packet_map.copy()
            self.input.frame_packet_map = {}
            self._add_input_to_session(self.input)
            new_frame_packet_map = {}
            for frame_num, instance_list in frame_packet_map.items():
                model_manager = ModelManager(session = self.session,
                                             instance_list_dicts = instance_list,
                                             member = self.member,
                                             project = self.project)
                model_manager.check_instances_and_create_new_models()
                new_frame_packet_map[frame_num] = instance_list
            # Replace with the instance list that has model_ids and run_ids

            self.input.frame_packet_map = new_frame_packet_map
        elif self.input.media_type == 'image':
            if not self.input.instance_list or self.input.instance_list.get('list') is None:
                return
            instance_list = self.input.instance_list['list'].copy()
            self.input.instance_list = {}
            model_manager = ModelManager(session = self.session,
                                         instance_list_dicts = instance_list,
                                         member = self.member,
                                         project = self.project)
            model_manager.check_instances_and_create_new_models()
            # Replace with the instance list that has model_ids and run_ids
            self.input.instance_list = {'list': instance_list}

        self._add_input_to_session(self.input)
        self.try_to_commit()

    def process_video(self):

        global New_video  # important

        try:
            print(New_video)
        except:
            from methods.video.video import New_video

        new_video = New_video(
            session = self.session,
            project = self.project,
            input = self.input
        )

        # TODO Would prefer to just pass input here
        # Not redeclaring

        try:
            self.populate_new_models_and_runs()
            file = new_video.load(
                video_file_name = self.input.temp_dir_path_and_filename,
                original_filename = self.input.original_filename,
                extension = self.input.extension,
                input = self.input,
                directory_id = self.input.directory_id)


        except Exception as e:
            self.input.status = 'failed'
            self.log['error']['process_video'] = f"Failed To process video: {traceback.format_exc()}"
            self.input.update_log = self.log
            logger.error(f"Failed To process video: {traceback.format_exc()}")

        self.clean_up_temp_dir_on_thread()

    def clean_up_temp_dir_on_thread(self, wait_time = 0):

        # cast as string since we don't want to keep session hanging around
        temp_dir_copy = str(self.input.temp_dir)
        t = threading.Timer(wait_time, clean_up_temp_dir, args = (temp_dir_copy,))
        t.daemon = True
        t.start()

    @staticmethod
    def determine_media_type(
        extension,
        allow_csv = True,
        input_type = None):
        """
        Maps filenames to "media_type" concept in Diffgram system
        Arguments:
            extension, String, assumed to have "." in front, ie ".jpg"
        Returns:
            String or None
       
        Not sure if we want to do lower()
        here or before storing on Input
        or both?
        """
        extension = extension.lower()

        if extension in images_allowed_file_names and input_type != 'from_geo_tiff':
            return "image"

        if extension in videos_allowed_file_names:
            return "video"

        if extension in text_allowed_file_names:
            return 'text'

        if extension in audio_allowed_file_names:
            return 'audio'

        if extension in csv_allowed_file_names:

            # TODO maybe log this or something
            if allow_csv is False:
                return None

            return "csv"

        if input_type is not None and input_type == 'from_sensor_fusion_json':
            if extension in sensor_fusion_allowed_extensions:
                return 'sensor_fusion'
        if input_type is not None and input_type == 'from_geo_tiff':
            if extension in geo_tiff_allowed_extensions:
                return 'geo_tiff'

        if extension in existing_instances_allowed_file_names:
            return "existing_instances"

        return None


# Get Media name and Extension from the URL
def get_file_name_and_extension(url, input_original_filename = None):
    """
    This assumes that the URL is in the format of
    https: ... a/b/c/filename.extension?otherstuff
    Where after the extension it's using "?"
    instead of /

    For extension,
    logic is that we still need to split on the first .
    but then also need to clear out the stuff after the "?"

    we are still expecting the extension with a leading "."

    Theory is if the extension somehow doesn't exit then it will try to return None?
    ie
    >>> after_last_slash.split(".")
    ['', '?2123123']

    >>> x.split(".")
    ['asdasd']

    At the moment this assumes that only a "?"
    can be after the filename (or )


    """
    extension = None
    # Remove query params from url
    if '?' in url:
        url = url.split('?')[0]
    after_last_slash = url.split('/')[-1]
    period_split = after_last_slash.split('.')
    file_name = period_split[0]

    if len(period_split) != 1:
        questionmark_split = period_split[1].split('?')

        # Python split returns the whole string
        # if nothing after split so we don't need to check
        # len again here.
        extension = questionmark_split[0]

        # Formatting, we expect None if it doesn't exist
        # in reasonable form
        if extension == '':
            extension = None
        else:
            extension = f".{extension}"

    file_name = secure_filename(file_name)
    if input_original_filename is not None:
        filename, file_extension = os.path.splitext(input_original_filename)
        return filename, file_extension
    else:
        return file_name, extension


def clean_up_temp_dir(path):
    # Race condition for thread accessing directory
    # (process_frame_core needs input.temp_dir)
    # This runs after last thread is kicked off, so sleep for a bit to before removal
    # Return success status anyway here so should be ok...

    gc.collect()

    time.sleep(240)
    logger.info("Running clean up")
    logger.info(path)
    try:
        shutil.rmtree(path)  # delete directory
        logger.info("Cleaned successfully")
    except OSError as exc:
        logger.error(f"shutil error {str(exc)}")
        pass
