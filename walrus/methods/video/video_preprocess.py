# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *

import gc
import shutil
import os
import subprocess

from shared.data_tools_core import Data_tools

"""
NOTE to test this, can just look at 
temp folder that has splits, since if there is an issue
here it's not with the per video processing but with the 
"splitting" which is visible here.
	
	Alternatively can look at cloud storage,
	but much easier debugging wise to look at temp dir

"""
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from shared.database.input import Input

data_tools = Data_tools().data_tools


@dataclass
class Video_Preprocess():
    session: Any
    parent_input: Input

    def __post_init__(self):
        self.log = regular_log.default()
        self.project = self.parent_input.project

        self.previous_file_size = -float('inf')

        self.do_upload = True  # ie set to False to skip upload for testing

    def split_video(self):
        """
        Create input id upfront so we can save to matching folder
        then trigger processing deferred after upload is complete?
        """

        # ie in this case it's a "known" thing so it should
        # be able to use our own app engine download operation...

        self.offset_in_seconds: int = 0

        # TODO handle "last" case if that matters? or does ffmpeg handle
        # if endtime > video time
        # Do we actually need to know the duration in advance
        # Can we just loop till exception?
        """

        We make assumptions that small files will return False
        so we will usually stop early

        This assumption is baed on file size, see notes in self.split

        The number of times we run this is a "magic" number of sorts
        200 means a 3 hour video with 60 seconds per split for example.

        """
        logger.info("Running Split")

        for i in range(200):
            # magic number of "cap" to number of clips here
            result = self.split(i)
            if result is False:
                break

        # For now success compelte just means it has split the clips...

        self.parent_input.status = "success"
        self.parent_input.percent_complete = 100

    def check_ok_to_split(self):
        """
        ie running this prior to running split_video

        Can disable by setting Input.video_split_duration to 0.

        We need this check, even if we didn't do any of the other stuff,
        because need a way to disable it, now that we set a default value.

        Success cases:
        * Video length is > then split duration
        * Failed to read length

        We are assuming that if say split is set to 30,
        but user uploads a 10 second video, we don't want to split it.

        We try to check the length using meta data ie ffprobe
        We assume if that check fails (and it's not user disabled)
        then we do still want to split it.

        I'm not really sure if we need this check, since the user can disable
        it by setting it to 0, but directionally was trying to make that
        a little "smarter" I guess...

        Yes could do if not but just feel this is more readable...

        JAN 27, 2020
            New plan is if we can't detect the video length from this here
            we DON'T split the video because it seems like split is causing more
            issues then it's solving at this point

        # TODO maybe log why it wasn't split?

        """
        if self.parent_input.video_split_duration is None:
            return False

        if self.parent_input.video_split_duration == 0:
            return False

        duration_in_seconds = self.get_length(
            filename = self.parent_input.temp_dir_path_and_filename)

        # See Jan 27 note above
        if duration_in_seconds is None:
            return False

        if duration_in_seconds < self.parent_input.video_split_duration:
            return False

        logger.info("OK to Split")

        return True

    def get_length(self, filename):
        """
        https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python

        """
        try:
            duration_in_seconds = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1",
                filename],
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT)

            # print("get_length", float(duration_in_seconds.stdout))

            return float(duration_in_seconds.stdout)

        except Exception as exception:
            print("get_length exception ", exception)
            return None

    def split(self, i: int):
        """
        note that filename vs local path vs blobpath are all different!
        """

        end_time = self.offset_in_seconds + self.parent_input.video_split_duration

        # These are the actual file names and paths
        # the blob path is based on input id and deteremined at new input.
        # keep in mind this changes for each of the clips
        # so no point storing it on the parent
        # and don't want to store it on the child because
        # the child will re download it (potentially on a different machine)

        """
        Feb 8 2020
            Had issues where duration was wrong
            Observe that it copies the existing codec when saving
            Tested and did not change it
            Realized local machine working probably means some issue
            with server side version for ffmpeg.

        """

        # Feb 9 2020, original_filename does NOT include extension.
        # Careful here, ffmpeg needs a valid extension otherwise throws error
        new_sub_clip_filename = str(self.offset_in_seconds) + "_" + \
                                self.parent_input.original_filename

        output_temp_local_path = f"{self.parent_input.temp_dir}/{new_sub_clip_filename}"

        try:
            ffmpeg_extract_subclip(
                self.parent_input.temp_dir_path_and_filename,
                self.offset_in_seconds,
                end_time,
                targetname = output_temp_local_path)
            logger.info(f"{str(i)} (Iteration) ffmpeg_extract_subclip Success")
        except Exception as e:
            self.log['info'] = f"Last iteration: {str(i)}"
            logger.error(f"Error splitting video {str(e)}")
            return False

        """
        It appears that ffmpeg does not detect if there's no "real"
        data to be read. So we observe that the "last" files, if less than 
        a certain size probably not a real file.

        When looking at the temp dir see one that are 108 KB (108,000 B)
        Aren't real files?

        Jan 24, 2020 note this seems to change when we did the "fix" 
        for adjusting the split as described here
        https://github.com/swirlingsand/ai_vision/commit/b7c0aa3891eb89fa76ad2666137bf7469dcbeab9

        Size example
        then previous file size is size, ie 1000
        >>> 10 < (1000/10)
            True

        ie 750 / 15 = 50
        so a 25 mb would return False
        but another 750 would just update it

        size < ( self.previous_file_size / 15):
        is the correct condition 

        but init case is different
        previous size init inf / 10 == inf
        so first size will always be true,
        BUT we don't want to return on the first one
        SO we do minus inf
        Because 2000 < ( -float('inf') / 15) will almost always be False

        And it's cleaner to do that then have a special case for first pass.

        In the odd case that the / 10 comparison misses,
        we have the == to comparison, so it doesn't keep repeating a bunch of equal size files

        As an automatic oracle to test this could look
        at a predefined number of expected files in folder 
        (assuming that the video file and split duration were known)

        """
        size = os.stat(output_temp_local_path).st_size  # in bytes

        if size < (self.previous_file_size / 10) or size == self.previous_file_size:
            return False
        else:
            self.previous_file_size = size

        # this must be before we upload so we get the id
        self.new_input()
        logger.info(f"{str(i)} (Iteration) new_input finished")

        # Copy the frame packet map if exists.
        self.input.instance_list = self.parent_input.instance_list
        self.input.frame_packet_map = self.parent_input.frame_packet_map
        self.input.original_filename = new_sub_clip_filename

        if self.do_upload is True:
            data_tools.upload_to_cloud_storage(
                temp_local_path = output_temp_local_path,
                blob_path = self.input.raw_data_blob_path,
                content_type = f"video/{self.parent_input.extension}"
            )
            logger.info(f"{str(i)} (Iteration) upload_to_cloud_storage finished")

        # Should be able to run right after upload
        # Double check this is just the path and not whole dir..
        # otherwise may need to be later
        self.clean_up_temp_dir(output_temp_local_path)

        # By setting the input to processed deffered
        # it is placed in the master queue
        # This must be after it's uploaded so we know it's
        # Available
        self.input.processing_deferred = True

        # We want to store this here because
        # it will be different for each video that's split
        # And we haven't created the class Video element
        # for it until it hits actual processing
        self.input.offset_in_seconds = self.offset_in_seconds

        # TODO instead of updating all the way here
        # As the child videos come through
        # detect if parent, and then update accordingly?
        if not self.parent_input.percent_complete:
            self.parent_input.percent_complete = 0
        self.parent_input.percent_complete += 1
        self.session.add(self.parent_input)

        self.try_to_commit()

        # TODO clean up extracted clip?

        # Could do a - 1 or something for splitting it but
        self.offset_in_seconds = end_time

        logger.info(f"{str(i)} split overall function Success")

        return True

    def new_input(self):
        """
        Careful for video_split_duration...shouldn't add it
        since we condition on it

        NOTE here we have self.parent_input available
        as stored on Video Preprocess class but parent_input is not available
        on a generic input object see notes in Input class
        """

        self.input = Input.new(
            parent_input_id = self.parent_input.id,
            project = self.project,
            media_type = "video",
            type = "from_video_split",
            job_id = self.parent_input.job_id,
            directory_id = self.parent_input.directory_id
        )

        self.session.add(self.input)
        self.session.flush()

        # Do we need .mp4 on end here?
        self.input.raw_data_blob_path = settings.PROJECT_VIDEOS_BASE_DIR + \
                                        str(self.project.id) + "/raw/" + str(self.input.id)

        self.extension = ".mp4"

    def try_to_commit(self):

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def clean_up_temp_dir(self, path):

        # print(path)
        try:
            shutil.rmtree(path)  # delete directory
        # print("Cleaned successfully")
        except OSError as exc:
            # print("shutil error")
            pass
