# OPENCORE - ADD
from methods.regular.regular_api import *
import os

import threading
# only on machines not following docker file and don't have ffmpeg
# imageio.plugins.ffmpeg.download()
import shutil
import tempfile

import moviepy.editor as moviepy_editor

from shared.database.image import Image
from shared.helpers.permissions import getUserID
from shared.database.user import UserbaseProject

from shared.database.video.video import Video
from shared.database.video.sequence import Sequence
from shared.database.input import Input

from methods.input import process_media
from shared.data_tools_core import Data_tools


# Design doc

class FrameCompletionControl:
    """
        Small Data structure for controlling the pending vs processed frames
        in a more granular way.
    """

    def __init__(self):
        self.frames_completed_data = {}
        self.completed_frames = 0

    def mark_frame_complete(self, frame_num):
        self.frames_completed_data[frame_num] = True
        self.completed_frames += 1

    def add_pending_frame(self, frame_num):
        self.frames_completed_data[frame_num] = False

    def get_total_frames(self):
        return len(self.frames_completed_data.keys())


class New_video():
    """
    1. Get video file (in temp directory)
    2. Do work

    TODO better way to batch sessions
    """

    def __init__(
        self,
        session,
        project,
        input
    ):

        self.session = session
        self.project = project
        self.input = input

        self.found_sequences = {}
        self.sequence_number_to_id = {}
        self.highest_frame_encountered = None

    def upload_video_file(
        self,
        video_file_name,
        extension,
        video):

        video.file_blob_path = settings.PROJECT_VIDEOS_BASE_DIR + \
                               str(self.project.id) + "/" + str(video.id)

        data_tools = Data_tools().data_tools
        data_tools.upload_to_cloud_storage(
            temp_local_path = video_file_name,
            blob_path = video.file_blob_path,
            content_type = "video/" + str(extension[1:]),
            timeout = 60 * 10
        )

        video.file_signed_url = data_tools.build_secure_url(video.file_blob_path, 2592000)

    def load(self,
             video_file_name,
             original_filename,
             extension,
             input: Input,
             directory_id = None):
        """

        Convert to .mp4 format if needed
        Upload .mp4 video
        Process each frame

        Arguments
            video_file_name, String, complete file path including directory, filename, and extension
            original_filename, String
            extension, String, includes ".", ie ".mp4"

        Returns
            None
        """

        try:
            clip = moviepy_editor.VideoFileClip(video_file_name)
            input.status = "loaded_video"
            input.time_loaded_video = datetime.datetime.utcnow()
            input.percent_complete = 20.0
            self.try_to_commit()

        except Exception as exception:
            input.status = "failed"
            input.status_text = "Could not load video. Try again, try a different format or contact us."
            # only for internal use
            # could look at storing in DB later or Using event logging.
            print(input.status_text, input.id, exception)
            return None

        # https://stackoverflow.com/questions/43966523/getting-oserror-winerror-6-the-handle-is-invalid-in-videofileclip-function
        clip.reader.close()
        # Audio thing here too still doesn't seem to fix it...
        # clip.audio.reader.close_proc()

        # fps handling
        fps = self.project.settings_input_video_fps

        if fps is None:
            fps = 5

        if fps < 0 or fps > 120:
            input.status = "failed"
            input.status_text = "Invalid fps setting of " + fps
            return None

        original_fps = clip.fps  # Cache, since it will change

        """
        Context here is that a user may set FPS to be say 60
        but if the video is only 30 FPS, we just want to use that not convert it

        TODO feel like this could be merged with FPS == 0? feels a bit funny still
        Also not quite clear if there's value of using the set_fps() function in this case
        or if we should skip that

        """

        print('fps', fps, 'original_fps', original_fps)
        if fps > original_fps:
            # print("Using original fps because proposed fps is higher."
            #	  "original_fps:", original_fps)
            fps = original_fps

        # TODO log this instead of printing it
        # print("original length", int(clip.duration * original_fps))

        if fps == 0 or fps == original_fps:
            # 1)  == 0 is flag for conversion disabled
            # 2) == original_fps, we are using the "original" FPS, so there is no conversion
            # This could be because of the > check or some other reason.

            fps_conversion_ratio = 1
            # keep in mind we store "fps" below on other stuff...
            # so should make sure this is up to date
            fps = original_fps  # case of setting to 0 to disable

        else:

            fps_conversion_ratio = original_fps / fps

            clip = clip.set_fps(fps)
        # https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html#moviepy.video.VideoClip.VideoClip.set_fps
        # Returns a copy of the clip with a new default fps for functions like write_videofile, iterframe, etc.

        # TODO do we want to save original

        # note these statements need to be after here in order to make sure
        # we update fps properly
        # otherwise have fps of say 0 and it's funny
        print("new length", int(clip.duration * fps))

        length = int(clip.duration * fps)  # Frame count (ESTIMATED) otherwise requires iteration / loop to get exact

        # temp higher limit for testing stuff
        # enough for a 120fps 5 minutes, or 60 fps 10 minutes
        frame_count_limit = 36000

        if length > frame_count_limit:
            input.status = "failed"
            input.status_text = "Frame count of " + str(length) + \
                                " exceeded limit of " + str(frame_count_limit) + " (per video)" + \
                                " Lower FPS conversion in settings, split into seperate files, or upgrade account."
            return None

        max_size = settings.DEFAULT_MAX_SIZE

        if clip.w > max_size or clip.h > max_size:
            clip = resize_video(clip)

        video_file_name = os.path.splitext(video_file_name)[0] + "_re_saved.mp4"

        print(clip.fps)

        if settings.PROCESS_MEDIA_TRY_BLOCK_ON is True:
            try:
                # See https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html?highlight=write_videofile#moviepy.video.io.VideoFileClip.VideoFileClip.write_videofile
                # And https://github.com/Zulko/moviepy/issues/645
                #	BUT note it's been renamed to "logger"

                # TODO maybe capture log output somewhere else for debugging?
                # Maybe we could use log to update input status / percent complete

                """
                Feb 9 2020 Audio to True seems to add issues
                ie : index -100001 is out of bounds for axis 0 with size 0 ffmpeg
                found this
                but I don't think that's it
                https://stackoverflow.com/questions/59358680/how-to-fix-out-of-bounds-error-in-to-soundarray-in-moviepy
            
                The strange part is that some of it works...
                TODO IF audio is a common issue, could have 2 try blocks
                but would want to have this as a function then.
                ie video with no audio is perhaps better then total failure, or total no audio.
                """

                clip.write_videofile(video_file_name,
                                     audio = False,
                                     threads = 4,
                                     logger = None
                                     )
            except Exception as exception:
                input.status = "failed"
                input.status_text = "Could not write video file. Try a different format or contact us."
                print(input.status_text, input.id, exception)
                return None

        else:
            clip.write_videofile(video_file_name,
                                 audio = False,
                                 threads = 4,
                                 logger = None
                                 )

        # print(video_file_name)

        if not directory_id:
            directory_id = self.project.directory_default_id

        # Video file gets created in advance so
        # be careful to add project here

        """
        This is in the context of Video potentially wanting more stuff from the 
        "parent video".
        This needs a lot of work. For the moment we just get the parent input
        and copy a single attribute here for easier access later on.
        Directionally we want to think about stronger connections between
        split clips.
        And forest wise we need to grab this here because going back to get the input
        afterwards from file can be challenging becasue as the system does
        various modifications the parent gets further and further removed.
        """

        parent_video_split_duration = None
        try:
            parent_input = input.parent_input(self.session)
            if parent_input:
                parent_video_split_duration = parent_input.video_split_duration
        except:
            print("Could not get parent input")

        video, input.file = Video.new(
            session = self.session,
            project = self.project,
            filename = original_filename,
            frame_rate = clip.fps,
            frame_count = 0,
            width = clip.w,
            height = clip.h,
            directory_id = directory_id,
            parent_input_id = input.parent_input_id,
            parent_video_split_duration = parent_video_split_duration)

        if self.input.frame_packet_map:
            self.__prepare_sequences(parent_input = input)
            if self.check_update_log_errors() is False: return

        input.file.input_id = input.id  # revsere link is sometimes handy to have.

        # Jan 13, 2020 these are both computed above
        # Video object is not created yet so stored locally and then used here...
        video.original_fps = original_fps
        video.fps = fps
        video.fps_conversion_ratio = fps_conversion_ratio
        video.offset_in_seconds = input.offset_in_seconds

        video.root_blob_path_to_frames = settings.PROJECT_IMAGES_BASE_DIR + \
                                         str(self.project.id) + "/" + str(video.id) + "/frames/"

        self.upload_video_file(video_file_name, ".mp4", video)

        input.status = "finished_writing_video_file"
        input.time_video_write_finished = datetime.datetime.utcnow()
        input.percent_complete = 30.0

        self.try_to_commit()

        self.session.add(video)
        for index, frame in enumerate(clip.iter_frames()):
            global_frame_number = frame
            if input.type == 'from_video_split':
                seconds_offset = input.offset_in_seconds
                offset_in_frames = video.fps * seconds_offset
                global_frame_number = frame + offset_in_frames

            if index == 0:
                input.status = "pushing_frames_into_processing_queue"

            # This setups up input, see function below
            self.add_frame_to_queue(
                frame,
                index,
                original_filename,
                self.project,
                directory_id,
                video,
                length,
                input.file,  # assumes this is video_parent_file
                global_frame_number)

            # TODO clarify if this is actually showing up the queue as expected
            video.frame_count += 1

            # This is really key for monitoring efforts
            # Because at the moment this loop can be fairly slow

            if index % 10 == 0:
                # Where 10 is adding this every 10 frames
                # to be completed by next phase
                # at most this adds 1 when compelte so multiple by 30 to represent
                # this portion of the work
                input.percent_complete += (10 / length) * 30
                self.try_to_commit()

        # Clean up handled in process media..

        input.time_pushed_all_frames_to_queue = datetime.datetime.utcnow()

        return input.file

    def try_to_commit(self):

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def check_update_log_errors(self):

        # Missing Case
        if not self.input.update_log:
            logger.info("Update Log is None.")
            return True

        # Error Case
        if len(self.input.update_log["error"].keys()) >= 1:
            return False

        # Success / Default Case
        return True

    def update_from_frame_packet_map(
        self):
        """
        Handles prep work, and then pushing input items into queue for each frame

        Does not require all frames to exist
        Uses 'update' mode, which assumes that most of the normal "input processing" work will
        be skipped
        """

        self.__prepare_sequences(parent_input = self.input)

        if self.check_update_log_errors() is False: return

        self.try_to_commit()  # 1/2 needed otherwise foreign key violation because
        # 2/2 new sequences won't exist yet

        for frame_number, instance_list in self.input.frame_packet_map.items():
            input = self.__format_frame_for_update(
                frame_number = frame_number,
                parent_input = self.input)

            self.__push_formatted_frame_to_queue(
                input = input)

        return True

    def __prepare_sequences(
        self,
        parent_input):

        self.determine_unique_sequences_from_external()
        self.create_all_found_sequences(video_file_id = parent_input.file.id)
        if self.check_update_log_errors() is False: return
        self.add_sequence_id_to_instances()
        if self.check_update_log_errors() is False: return

    def __format_frame_for_update(
        self,
        frame_number: int,
        parent_input: Input
    ):
        """
        frame may or may not exist yet

        """
        input = Input.new(
            project = None,  # required, but see project_id  detached session below.
            media_type = "frame")

        frame_number = int(frame_number)  # cast to avoid future problems

        input.project_id = self.project.id  # Avoids detached session issues for parallel processing
        input.mode = "update"
        input.parent_input_id = parent_input.id
        input.parent_file_id = parent_input.file.id  # Assume downstream process will use this to get frame
        input.frame_number = frame_number
        input.video_parent_length = self.highest_frame_encountered

        # Returns input because it does formatting too, TODO adjust function name
        input = self.get_instance_list_from_packet_map(
            input = input,
            frame_number = frame_number)

        return input

    def __push_formatted_frame_to_queue(
        self,
        input: Input):

        item = process_media.PrioritizedItem(
            input = input,
            media_type = input.media_type,  # declaring here helps with routing
            priority = 100 + input.frame_number,  # Process in frame priority
            frame_number = input.frame_number  # Careful, downstream process currently expects it
        )

        process_media.add_item_to_queue(item)

    def add_frame_to_queue(
        self,
        frame,
        index: int,
        original_filename: str,
        project: Project,
        directory_id,
        video,
        length,
        video_parent_file: File,
        global_frame_number = None):
        """
        Where frame is:
            a HxWxN np.array, where N=1 for mask clips and N=3 for RGB clips.
            https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html


        Careful we don't have self. context here

        Cautions
            * We purposely do not not pass the job id, since we only want to original
            video to be added to the job

        Question,
            is it correct we create input class in part to maintain
            same concepts / format even for video frames?
            Answer: For example see frame_end_number is used to pass information
                Makes more sense to have it all in there then the PrioritizedItem() thing
                long term
                Also thinking in terms of logging
                And yes of course, then it's complete reuse of the component


        Jan 20, 2020
            Note we purposely do NOT commit this as it creates unneeded
            db overhead, so instead we only use it as a local object
            to maintain consistency of design

            which means we do NOT want to add to add it a sesion
            ie self.session.add(input)
        """

        input = Input()

        # Use input for class attributes,
        # but don't add it to the session for video?

        # TODO use File.new() for consistency here (ie as we add new things)

        # Single frame naming
        input.original_filename = original_filename + "_" + str(index)
        input.extension = ".jpg"
        input.media_type = "frame"

        input.temp_dir = tempfile.mkdtemp()
        input.project = project
        input.directory_id = directory_id
        input.parent_file_id = video_parent_file.id

        # caution length is estimated. frame_count
        # is calculated as we roll through this so can't use it yet
        # Question: clarity on difference between numbers.
        # (I know estimate but still.)
        input.video_parent_length = length
        input.parent_input_id = self.input.id
        input.project_id = self.project.id

        # This is a temporary usage thing only
        # Note database persisted
        # Context of needing it to be defined so existing instances
        # Can use it (vs having to get video from db each time,
        # prior we defined this on first frame.
        input.root_blob_path_to_frames = video.root_blob_path_to_frames

        input = self.get_instance_list_from_packet_map(
            input = input,
            frame_number = index,
            global_frame_number = global_frame_number)

        """
        For frame priority, the original genesis was doing the last frame last
        but, I think it also makese sense to process in order in general.
        An alternative would be to say put a flag on the last frame
        but using order feels like a more general solution, assuming no suprises
        or extra overhead.


        Storing frames

        Maybe don't attach video_parent_file
        because it leads to not bound errors in ORM fairly easily.

        """

        # TODO, consider sending data as a "raw" blob
        # to cloud storage, then setting "processing deferred" to True here.

        # Process frames of videos started before new videos
        item = process_media.PrioritizedItem(
            priority = 100 + index,  # Process in frame priority
            input = input,
            raw_numpy_image = frame,
            file_is_numpy_array = True,
            video_id = video.id,
            frame_number = index,
            global_frame_number = global_frame_number,
            media_type = input.media_type
        )

        process_media.add_item_to_queue(item)

    # TODO use this video attributes
    # content_type = None,

    def get_instance_list_from_packet_map(
        self,
        input,
        frame_number: int,
        global_frame_number = None):
        """
        Helper function to format nicely

        Theory that while we are processing a video,
        we do this upfront in order to be able to process each list seperetly.

        Strange frame_number isn't available on input (because it's on the PrioritizedItem class)

        'frame_packet_map' : {
                0 : instance_list,
                6 : instance_list,
                9 : instance_list
            }


        Caution some potential gotcahas with the key being a string
        or int here.
        """

        if self.input.frame_packet_map:

            input.instance_list = {}
            if input.type == 'from_video_split':
                instance_list = self.input.frame_packet_map.get(str(global_frame_number))
            else:
                instance_list = self.input.frame_packet_map.get(str(frame_number))
                
            if instance_list is None:
                instance_list = self.input.frame_packet_map.get(int(frame_number))

            if instance_list:
                input.instance_list['list'] = instance_list

        # print("frame_number", frame_number, input.instance_list['list'])
        # could create sequences here...
        print('GETTING FROM FRAME PACKET MAPPPPP', input.instance_list)
        return input

    def determine_unique_sequences_from_external(self):
        """
        Careful the sequences are unique per label_file_id

        In a sense this makes the assumption we would rather do this here
        then a bunch of database calls to see if it exists or not

        Another idea was tracking keyframes here...
            but seems more repeatable to use regenerate method...
            could still cache instances as they are being created for that...


            highest_frame_encountered
                context of wanting to know when to update sequence/
                when processing is finished / percent complete.
                in normal video context this is just the total frames
                but here it's arbitrary, eg someone could update
                only frame 20 in a 200 frame video.

        Careful, self.input in this context is the PARENT video input
        See __format_frame_for_update() for FRAME input updates.

        """

        if not self.input.frame_packet_map:
            return

        self.highest_frame_encountered = 0

        # print(self.input.frame_packet_map)
        for frame_number, instance_list in self.input.frame_packet_map.items():

            self.determine_new_sequences_from_instance_list(
                instance_list = instance_list)

            if int(frame_number) > self.highest_frame_encountered:
                self.highest_frame_encountered = int(frame_number)

        # Careful need to pass this to child inputs too
        logger.info("found_sequences " + str(self.found_sequences))

    def determine_new_sequences_from_instance_list(
        self,
        instance_list):
        """
        Problem
            Timing issue of when sequences are created

        Idea
            Create sequences upfront.

        """

        for instance in instance_list:

            number = instance.get('number', 1)
            label_file_id = instance.get('label_file_id')

            # TODO handle maybe flagging error up more here...
            # logger.info((number, label_file_id))
            if number and label_file_id:

                if label_file_id not in self.found_sequences:
                    self.found_sequences[label_file_id] = set([int(number)])

                elif number not in self.found_sequences.get(label_file_id):
                    self.found_sequences[label_file_id].add(int(number))

    def create_all_found_sequences(self, video_file_id):

        if not self.found_sequences:
            logger.info("No sequences found")
            return

        for label_file_id, number_set in self.found_sequences.items():

            for number in number_set:

                self.create_sequences_not_yet_existing(
                    video_file_id = video_file_id,
                    label_file_id = int(label_file_id),
                    number = int(number)
                )

                if self.check_update_log_errors() is False:
                    self.input.status = "failed"
                    self.input.status_text = "See Update Log"
                    return

    def add_sequence_id_to_instances(self):
        """

        April 8, 2020

        in context of parallel processing so not wanting to have to
        hit DB every time to get sequence_id (since we already know it).

            Also motivated that the current "update" context has side effects (sorta)
            so we would have to abstract the sequence_id update part

        Realizing we want to move away from needing set of (label_file_id, number)
        but that's how current system works so rolling with it for now.

            Would like to move to number being unique per video, and a
            sequence being able to have multiple labels associated with it.

        """

        for frame_number, instance_list in self.input.frame_packet_map.items():

            for instance in instance_list:

                if 'sequence_id' not in instance:

                    number = instance.get('number', 1)
                    label_file_id = instance.get('label_file_id')
                    if label_file_id is None:
                        self.input.update_log['error'][str(frame_number)] = "At frame " + str(frame_number) + \
                                                                            "An instance is missing the label_file_id"
                        return

                    joint_key = (label_file_id, number)
                    instance['sequence_id'] = self.sequence_number_to_id.get(joint_key)
                    logger.info(instance['sequence_id'])

                    # NOTE if we get here, it's quite likely the issue is in the way we are
                    # determine_new_sequences_from_instance_list()   eg that set isn't mutating it or something
                    # Had issue where >>> set(str(12)) is {'1', '2'} which then caused this to fail.
                    # But just in case we have this long debug thing...

                    if instance['sequence_id'] is None:
                        self.input.update_log['error'][str(frame_number)] = "[Sequence Match Error] At frame " + str(
                            frame_number) + \
                                                                            " the instance with label_file_id: " + str(
                            label_file_id) + " the number " + str(number) + \
                                                                            " does not match an available sequence. " + " available pairs are " + str(
                            self.sequence_number_to_id)
                        logger.info(self.input.update_log['error'])
                        return

            self.input.frame_packet_map[frame_number] = instance_list

    def push_frames_for_copy_to_queue(
        self,
        source_video_parent_file_id,
        destination_video_parent_file_id):
        """
            Give the current data at self.input, get the video frame of the existing file
            and push them to the ProcessMedia Queue.
        :return:
        """

        source_video_frames = WorkingDirFileLink.image_file_list_from_video(
            session = self.session,
            video_parent_file_id = source_video_parent_file_id,
            order_by_frame = True
        )
        frame_completion_controller = FrameCompletionControl()
        for frame in source_video_frames:
            frame_completion_controller.add_pending_frame(frame.frame_number)

        for frame in source_video_frames:
            ### HOW TOD AVOID DETACHED SESSION
            ### Must only pass IDs and not pass any other objects

            # Actually the add remove link thing could be different too...

            # Careful the file id is the newly copied video
            # The previous video id should come from the NEW file id not the previous one
            frame_input = Input.new(
                parent_input_id = self.input.id,
                sequence_map = self.input.sequence_map,
                file_id = frame.id,  # existing
                video_parent_length = len(source_video_frames),
                directory_id = self.input.directory_id,
                source_directory_id = self.input.source_directory_id,
                remove_link = self.input.remove_link,
                add_link = self.input.add_link,
                copy_instance_list = self.input.copy_instance_list,
                parent_file_id = destination_video_parent_file_id,
                # This is the parent video file where all data is going to be copied.
                project_id = self.input.project_id,
                mode = 'copy_file',
                type = None,
                media_type = 'frame',
            )

            item = process_media.PrioritizedItem(
                input = frame_input,
                frame_completion_controller = frame_completion_controller,
                total_frames = source_video_frames[len(source_video_frames) - 1].frame_number,
                num_frames_to_update = len(source_video_frames),
                media_type = frame_input.media_type,  # declaring here helps with routing
                priority = 100 + frame.frame_number,  # Process in frame priority
                frame_number = frame.frame_number  # Careful, downstream process currently expects it
            )

            process_media.add_item_to_queue(item)
        return source_video_frames

    def add_sequence_map_to_input(
        self,
        source_video_parent_file,
        destination_video_parent_file_id):

        sequence_list = Sequence.list(
            session = self.session,
            video_file_id = source_video_parent_file.id)

        # This will map the new sequences old_id => new_id
        old_new_sequence_map = {}
        for sequence in sequence_list:
            sequence_copy = sequence.clone_sequence_with_no_instances(
                self.session,
                destination_video_parent_file_id = destination_video_parent_file_id)
            old_new_sequence_map[sequence.id] = sequence_copy.id

        # Add sequence map to parent input
        self.input.sequence_map = old_new_sequence_map
        return

    def create_sequences_not_yet_existing(
        self,
        video_file_id,
        label_file_id,
        number
    ):
        """
        We also create self.sequence_number_to_id because each instance
        needs a sequence_id to work as expected in downstream systems.
        Yet we cannot guarnatee that sequence_id existed prior as it may have just been created

        Sequences only apply relevant for videos (not images)

        In current context we enforce uniqinuess per label but trying to move away from that

        It's critical we get the sequence_id on the instance
        otherwise the preview image and various keyframe features will fail.
        """

        # Existing
        sequence = Sequence.get_from_video_label_number(
            session = self.session,
            video_file_id = video_file_id,
            label_file_id = label_file_id,
            number = number
        )
        if sequence:
            self.sequence_number_to_id[(label_file_id, number)] = sequence.id
            return

        # Caution note it needs file object not just int here

        label_file = File.get_by_id_and_project(
            self.session,
            self.project.id,
            label_file_id)

        # For now just hard return
        if label_file is None:
            self.input.update_log['error'][str(label_file_id)] = "Label File ID: " + str(label_file_id) + \
                                                                 "Does not exist in the project. Found at sequence Number: " + str(
                number)
            return

        sequence = Sequence.new(
            number = number,
            video_file_id = video_file_id,
            label_file = label_file
        )

        self.session.add(sequence)
        self.session.flush()  # For ID

        self.sequence_number_to_id[(label_file_id, number)] = sequence.id

        print("Created sequence")


def resize_video(clip):
    # TODO log rotation done?

    if clip.rotation in (90, 270):
        clip = clip.resize(clip.size[::-1])
        clip.rotation = 0

    # Caution, must match image size
    max_size = settings.DEFAULT_MAX_SIZE

    if clip.w > clip.h:
        if clip.w < max_size:
            width = clip.w
        else:
            width = max_size
        clip = clip.resize(width = width)
    else:
        if clip.h < max_size:
            height = clip.h
        else:
            height = max_size
        clip = clip.resize(height = height)

    return clip


# CAREFUL DANGEROUS FUNCTION
def migrate():
    with sessionMaker.session_scope() as session:

        video_file_list = session.query(File).filter(File.type == "video").all()

        frame_number = 0

        for file in video_file_list:
            image_file = session.query(File).filter(
                File.video_id == file.video_id,
                File.frame_number == frame_number).first()

            if image_file:
                file.video.preview_image_id = image_file.image_id
                session.add(file)
