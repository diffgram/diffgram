# OPENCORE - ADD
from methods.regular.regular_api import *
import math
from shared.database.video.sequence import Sequence

from scipy.interpolate import interp1d
import numpy as np

from shared.annotation import Annotation_Update
import traceback

# TODO maybe rename this is interfering with scipy namespace
class Interpolate():

    def __init__(self, session, project, video_file, log):

        self.session = session
        self.project = project
        self.video_file = video_file
        self.log = log

        self.member = get_member(session = session)

    def interpolate_all_sequences_in_video(self):
        """
        (All frames) Runs pipeline for frames to be interpolated

        Identify not yet modified key frames?

        - Start at 0
        - Find next keyframe
        - Interpolate between those keyframes
        - When at last keyframe, end

        """

        assert self.video_file is not None

        # Careful, the images should be sorted by frame number
        # And the instance list too...
        # Image list is needed for interpolated images (boxes can access image with box)

        """
         Caution, note that in the new syntax we call
         it video_parent_file_id and in the sequence
         it's valled video_file_id, but this should be 
         referring to same thing. 
        
        """

        sequence_list = self.session.query(Sequence).filter(
            Sequence.video_file_id == self.video_file.id,
            Sequence.single_frame == False,
            Sequence.archived == False
        ).all()

        self.log['sequence'] = {}

        if len(sequence_list) == 0:
            self.log['sequence']['error'] = {}
            self.log['sequence']['error']['error'] = 'No sequences. Click a label to open sequence navigator.'
            # Front end (as of 3/16/19 expects a sequence id as second key so double error key)
            return

        # QUESTION should we just use a standard serialization method for sequence?

        for sequence in sequence_list:
            self.interpolate_sequence(sequence)

        self.log['success'] = True

    def interpolate_sequence(
        self,
        sequence):
        """
        Process description

            1. Delete existing instances
            2.

        """

        self.prepare_sequence_log(sequence)

        if sequence.has_changes != True:
            return

        # TODO This is not checking for being an interpolated instance correctly?
        # ie it should have at least 2 KEYFRAME instances to interpolate

        if len(sequence.instance_list) <= 1:  # must have at least 2 instances to interpolate
            self.log['sequence'][sequence.id][
                'error'] = "Sequence must have at least 2 keyframe instances of type Box to interpolate"
            return

        # This is getting wrong count
        # self.log['sequence'][sequence.id]['keyframe_count'] = len(sequence.instance_list)

        instances_to_interpolate_list = []

        for instance in sequence.instance_list:

            # Delete old boxes
            if instance.interpolated is True:
                # TODO can't delete if through source control BUT
                # need to clarify what's actually getting deleted?
                # ie if not comitted can delete right?
                # soft delete becomes ungainly as it make interpolation slower with every pass...
                # AND if comitted, wouldn't copy interpolated ones anyway...

                # Careful, need this in 2 places
                # May be some files that get deleted but not recreated
                instance.file.set_cache_key_dirty('instance_list')
                self.session.delete(instance)

            # TODO issue here with instances
            # when editing
            if instance.interpolated is not True and \
                instance.soft_delete is not True and instance.frame_number is not None:
                instances_to_interpolate_list.append(instance)

        # Careful to sort by frame rate at some point in this process!!
        instances_to_interpolate_list.sort(key = lambda x: x.file.frame_number)

        self.__literal_interpolate_sequence(self.session,
                                            instances_to_interpolate_list,
                                            sequence)
        sequence.has_changes = False

    def prepare_sequence_log(
        self,
        sequence):

        self.log['sequence'][sequence.id] = {}
        self.log['sequence'][sequence.id]['number'] = sequence.number
        self.log['sequence'][sequence.id]['label_name'] = sequence.label_file.label.name
        self.log['sequence'][sequence.id]['has_changes'] = sequence.has_changes

    def interpolate_description(
        self):
        pass

    def __check_if_instance_list_ok_to_opreate_on(
        self,
        instance_list):

        if len(instance_list) < 2:
            return False

        return True

    # TODO use self.session
    def __literal_interpolate_sequence(
        self,
        session,
        instance_list,
        sequence):
        """
        Takes start and end points (annotations) and does interpolation

        Arguments:
            start, db box instance object
            end, db box instance object
        """

        # start = instance_list[index]
        # end = instance_list[index + 1]

        if not self.__check_if_instance_list_ok_to_opreate_on(
            instance_list = instance_list): return

        # Start and end must be in different frames?

        start = instance_list[0]
        end = instance_list[-1]

        # Length of instances != frames to interpolate
        # For example could have 4 keyframes and 68 frames to interpoalte over

        # Is this right? feel like we need to be more clear on "exclusive" vs "inclusive"
        # for key rames...

        frames_to_interpolate = abs(end.frame_number - start.frame_number)

        interpolation_description = "Start frame", start.frame_number, \
                                    "End frame", end.frame_number, \
                                    "Instances interpolated", frames_to_interpolate

        self.log['sequence'][sequence.id]['interpolation_description'] = interpolation_description

        # Segment is the division or "slice" that we are operating on
        # ie distance between 10 and 20 is 10. If there's 23 frames than
        # each segment is 10 / 23 or .43
        # Feel like this should be more generic ie for min vs max...

        # The first and last frames are keyframes, we already have data for them
        # ie frame 2 to 10, start at frame 3 and go to frame 9 (inclusive of 9)
        # So 10 - 2 = 8,

        for index, instance in enumerate(instance_list):
            self.__operate_on_sub_sequence(
                starting_instance = instance,
                index = index,
                instance_list = instance_list,
                sequence = sequence
            )

    def __operate_on_sub_sequence(
        self,
        starting_instance,
        index,
        instance_list,
        sequence
    ):

        min_points_x = []  # TODO clarify this is a list
        min_points_y = []
        max_points_x = []
        max_points_y = []

        # We change the new x segment with each new grouping of keyframes
        if index + 1 == len(instance_list):
            return

        # Because of slice notation we do 1 more then we want basically
        end_index = index + 2  # end slice notation
        # ie index >= len(x) then use last element like -1, actually slice handles this.

        # Careful that the end index for the spline is equal to (or greater)
        # than where we are interpolating too
        spline_instance_list = instance_list[index: end_index]

        start = instance_list[index]
        end = instance_list[index + 1]

        for instance in spline_instance_list:
            min_points_x.append(instance.x_min)
            min_points_y.append(instance.y_min)

            max_points_x.append(instance.x_max)
            max_points_y.append(instance.y_max)

        interpt_y_given_x_min = self.build_interpt_y_given_x(
            min_points_x,
            min_points_y,
            len(spline_instance_list))

        interpt_y_given_x_max = self.build_interpt_y_given_x(
            max_points_x,
            max_points_y,
            len(spline_instance_list))

        frames_to_interpolate = abs(end.frame_number - start.frame_number)
        if frames_to_interpolate < 1:
            return

        new_x_segment_min = abs(start.x_min - end.x_min) / frames_to_interpolate
        new_x_segment_max = abs(start.x_max - end.x_max) / frames_to_interpolate

        for interpolate_index in range(1, frames_to_interpolate):

            result, frame_index, new_instance_dict = self.__interpolate_specific_range_after_all_prep_done(
                start,
                end,
                new_x_segment_min,
                interpt_y_given_x_min,
                new_x_segment_max,
                interpt_y_given_x_max,
                interpolate_index
            )

            if result is False: continue

            self.__create_literal_annotations_after_known_good_new_instance(
                frame_index = frame_index,
                new_instance_dict = new_instance_dict,
                label_file_id = starting_instance.label_file_id,
                sequence = sequence)

    def __interpolate_specific_range_after_all_prep_done(
        self,
        start,  # object
        end,  # object
        new_x_segment_min,
        interpt_y_given_x_min,
        new_x_segment_max,
        interpt_y_given_x_max,
        interpolate_index):

        result_min, interpolated_y_min, new_x_min = self.interpolate_x_y(
            start.x_min,
            end.x_min,
            new_x_segment_min,
            interpt_y_given_x_min,
            interpolate_index)

        result_max, interpolated_y_max, new_x_max = self.interpolate_x_y(
            start.x_max,
            end.x_max,
            new_x_segment_max,
            interpt_y_given_x_max,
            interpolate_index)

        if result_min == "success" and \
            result_max == "success" and \
            start.frame_number <= end.frame_number:
            new_instance = {
                'y_min': interpolated_y_min,
                'x_min': new_x_min,
                'y_max': interpolated_y_max,
                'x_max': new_x_max
            }

            frame_index = start.frame_number + interpolate_index
            return True, frame_index, new_instance

        return False, None, None

    def __create_literal_annotations_after_known_good_new_instance(
        self,
        frame_index,  # int
        new_instance_dict,
        label_file_id,  # int
        sequence  # class Sequence
    ):

        # Annotation_Update is similar for all
        # frames, may be a way to reuse this object better
        video_data = {
            "video_mode": True,
            "video_file_id": self.video_file.id,
            "current_frame": frame_index
        }

        annotation_update = Annotation_Update(
            session = self.session,
            file = self.video_file,
            project = self.project,
            video_data = video_data,
            do_init_existing_instances = False,
            member = self.member  # Big performance improvement
        )

        annotation_update.update_instance(
            type = "box",
            x_min = new_instance_dict['x_min'],
            y_min = new_instance_dict['y_min'],
            x_max = new_instance_dict['x_max'],
            y_max = new_instance_dict['y_max'],
            label_file_id = label_file_id,
            number = sequence.number,
            sequence_id = sequence.id,
            interpolated = True
        )

        # Caution, may be existing files from another sequence
        # So we need to clear any new ones we create
        # (2/2 cases so far?) See deletion for other case
        annotation_update.file.set_cache_key_dirty('instance_list')

    def build_interpt_y_given_x(self,
                                points_x, points_y,
                                len_instance_list):
        """
        Builds a scipy interpolate 1d function

        Args:
            start_x, start_y, end_x, end_y  (TODO change this to accept array of points)
            frame_count, integer

        Returns:
            interpt_y_given_x, function
            new_x_segment, integer
        """
        # points = zip(points_x, points_y)

        # Sort list of tuples by x-value
        # points = sorted(points, key=lambda point: point[0])

        # Split list of tuples into two list of x values any y values
        # x1, y1 = zip(*points)

        x = np.array(points_x)
        y = np.array(points_y)

        kind = 'linear'
        if len_instance_list > 2:
            kind = 'zero'
        if len_instance_list > 3:
            kind = 'slinear'
        # if len_instance_list > 3:
        # kind = 'quadratic'
        # knots = interpolate.splprep([x, y])[0]
        # interpolated_y = interpolate.splev(points_x, knots, der=0)
        # print(interpolated_y)
        # return interpolated_y

        # print("kind", kind)
        try:
            interpt_y_given_x = interp1d(x, y, assume_sorted = False, kind = kind, fill_value = "extrapolate")
        except Exception as exception:
            print(exception)
            interpt_y_given_x = interp1d(x, y, assume_sorted = False, kind = 'linear', fill_value = "extrapolate")

        return interpt_y_given_x

    def interpolate_x_y(
        self,
        start_x,
        end_x,
        new_x_segment,
        interpt_y_given_x,  # function
        frame_index):
        """
        Given an x value function returns y value

        Interpolation handles y value changing positive/negative direction,
        given correct new_x value

        Args:
            start_x, end_x, integers
            new_x_segment, integer
            interpt_y_given_x, function
            frame_index, integer
        """

        if start_x <= end_x:  # Handle reversing direction for x

            # update x based on where we are in the index
            new_x = start_x + (new_x_segment * frame_index)
        else:
            new_x = start_x - (new_x_segment * frame_index)

        # interpolated_y = interpolate.splev(new_x, interpt_y_given_x, der=0)
        interpolated_y = interpt_y_given_x(new_x)

        # print(interpolated_y)
        if math.isnan(interpolated_y):
            return "error", None, None

        interpolated_y = int(interpolated_y)
        new_x = int(new_x)

        return "success", interpolated_y, new_x


# WIP WIP WIP
@routes.route('/api/walrus/video/interpolate',
              methods = ['POST'])
def interpolate_api(task_id):
    """
    Uses new permission through regular list system
        (that way can support the multiple permissions ie task / project)
    """

    spec_list = [
        {"task_id":
            {
                'kind': int,
                'permission': 'task'
            }
        },
        {"file_id":
            {
                'kind': int,
                'permission': 'project'
            }
        },
        {"sequence_id":
            {
                'kind': int,
            }
        }]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        # TODO get get file by id untrusted (can't remember the name)
        try:
            file = File.get_by_id_untrusted(
                project_string_id = task.project.project_string_id,
                file_id = task.file.id,
                with_for_update = True,
                nowait = True
            )
        except Exception as e:
            trace = traceback.format_exc()
            logger.error(f"File {task.file.id} is Locked")
            logger.error(trace)
            log['error']['file_locked'] = 'File is being saved by another process, please try again later.'
            return jsonify(log), 400
        if file.type != "video":
            return "File is not a video", 400

        # TODO get sequence

        return interpolate_api_shared(session, log, task.project, file)


# WIP WIP WIP
def interpolate_api_shared(
    session,
    project,
    video_file,
    sequence
):
    interpolate_diffgram = Interpolate(
        session = session,
        log = log,
        project = project,
        video_file = video_file)

    interpolate_diffgram.single()

    return jsonify(log = interpolate_diffgram.log), 200


# PENDING DEPRECREATION / REMOVAL  (In favor of single sequence)

@routes.route('/api/walrus/task/<int:task_id>'
              '/video/interpolate',
              methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def interpolate_all_frames_using_task(task_id):
    with sessionMaker.session_scope() as session:
        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        log = regular_log.default_api_log()
        try:
            file = File.get_by_id(
                session = session,
                file_id = task.file.id,
            )
        except Exception as e:
            trace = traceback.format_exc()
            logger.error(f"File {task.file.id} is Locked")
            logger.error(trace)
            log['error']['file_locked'] = 'File is being saved by another process, please try again later.'
            return jsonify(log), 400

        # could be a valid task id that's not a video
        if file.type != "video":
            return "Task file is not a video", 400

        return interpolate_api_shared(session, log, task.project, file)


# PENDING DEPRECREATION / REMOVAL   (In facvor of single sequence)

@routes.route('/api/walrus/project/<string:project_string_id>'
              '/video/single/<string:video_file_id>'
              '/interpolate',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def interpolate_all_frames(project_string_id, video_file_id):
    """

    This may be a long running operation for longer videos.
    Prior we had this start running on a new thread, but that doesn't really make sense since
    * The user likely wants to see results from this before proceeding
    * We want to make errors louder, ie not having enough instances etc.
    * For an "average" case it completes in less < 10 seconds so it's not really that long running

    """

    spec_list = [{'directory_id': int}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        directory = WorkingDir.get_with_fallback(
            session = session,
            project = project,
            directory_id = input['directory_id'])

        if directory is False or directory is None:
            print("Invalid directory")
            return jsonify("Invalid directory"), 400

        try:
            video_file = File.get_by_id_untrusted(
                session = session,
                user_id = None,
                project_string_id = project_string_id,
                file_id = video_file_id,
                directory_id = directory.id,
                with_for_update = True,
                nowait = True)
        except Exception as e:
            trace = traceback.format_exc()
            logger.error(f"File {video_file_id} is Locked")
            logger.error(trace)
            log['error']['file_locked'] = 'File is being saved by another process, please try again later.'
            return jsonify(log), 400

        return interpolate_api_shared(session, log, project, video_file)


def interpolate_api_shared(
    session, log, project, video_file):
    interpolate_diffgram = Interpolate(
        session = session,
        log = log,
        project = project,
        video_file = video_file)

    interpolate_diffgram.interpolate_all_sequences_in_video()

    return jsonify(log = interpolate_diffgram.log), 200
