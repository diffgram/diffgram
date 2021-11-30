import operator
from imageio import imread
from imageio import imwrite
import tempfile
import numpy as np

from methods.regular.regular_api import *
from shared.database.action.action_flow import Action_Flow, TIME_WINDOW_SECONDS_MAPPER
from shared.database.action.action_event import Action_Event
from shared.database.action.action_flow_event import Action_Flow_Event
from shared.database.image import Image
from shared.data_tools_core import Data_tools
from io import BytesIO
from PIL import Image as PIL_Image
from shared.database.notifications.notification import Notification


class Action_Pipeline():
    SUPPORTED_WINDOWING_EVENTS = ['task_completed', 'task_created', 'input_file_uploaded']

    def __init__(self,
                 session,
                 member,
                 project,
                 org,
                 log,
                 mode,
                 file,
                 flow=None,
                 trigger_event=None
                 ):

        self.session = session
        self.member = member
        self.project = project
        self.init_time = None
        self.org = org
        self.mode = mode
        self.log = log  # Question, if not running from http do we actually
        # want to use same logging thing or?

        self.flow = flow

        # Having a flow and flow id is just confusing?

        self.file = file
        self.trigger_event = trigger_event

        self.flow_event = None
        self.action_event = None  # This is just the "current" event.

        self.action = None  # Current

        self.flow_is_running = True

        self.previous_action_event = None
        self.previous_previous_action_event = None

    def get_flow(self):
        """
        Assume if flow gets passed then it's ok?
        """

        if not flow:

            self.flow = Action_Flow.get_by_id(
                session=self.session,
                id=self.flow_id,
                project_id=self.project.id)

            if self.flow is None:
                self.log['error']['flow_id'] = "Invalid flow_id"
                return

    def new_action_flow_event(self):

        # TODO Where is flow_id coming from

        self.flow_event = Action_Flow_Event.new(
            session=self.session,
            flow=self.flow,
            project=self.project,
            org=self.org,
            file=self.file
        )

    def new_action_event(self):
        """
        Assume this gets created for every action,
        and then action specific information can be added to
        self.action_event as needed?

        """

        # Caution requires bunch of stuff...

        # TODO how to load member, link other stuff..

        self.action_event = Action_Event.new(
            flow_event_id=self.flow_event.id,
            flow_id=self.flow.id,
            action_id=self.action.id,
            session=self.session,
            file_id=self.file.id if self.file else None,
            project_id=self.project.id,
            org=self.org,
            kind=self.action.kind
        )

    def sleep_for_aggregation_window_time(self):

        if not self.flow.time_window or self.trigger_event.type not in self.SUPPORTED_WINDOWING_EVENTS:
            return
        # We're saving in memory the init time. So when thread restart we can calculate the time diff.
        # Value is based on Actionflow event creation time.
        logger.debug('Sleeping flow for {}'.format(self.flow.time_window))
        self.init_time = self.trigger_event.aggregation_window_start_time
        time.sleep(TIME_WINDOW_SECONDS_MAPPER[self.flow.time_window])

    def start(self):
        """

        Given a new file in flow, kick start flow.
        "Special" action in that it "starts" it?

        Declares intial action

        Assumes always at least one action

        """
        logger.debug('Started Action pipeline {}'.format(self.flow.id))
        limit_actions = 20
        actions_counter = 0
        reset_aggg_time = False
        ### Setup
        self.action = self.flow.first_action

        self.new_action_flow_event()

        if self.action is None:
            self.flow_event.status = "failed"
            self.flow_event.status_description = "No first_action."
            return

        # Ignore run but Check if time has expired
        if self.trigger_event.has_aggregation_event_running:
            self.sleep_for_aggregation_window_time()

        while self.flow_is_running is True:

            ### MAIN
            # Go to next action based on flow

            # Future could abstract to go_to_next() as this expands

            if self.action is None:
                self.complete_flow()
                return

            print("Action", self.action.id, self.action.kind)

            self.run_action()
            ###

            # Just in case
            if actions_counter >= limit_actions:
                self.complete_flow()
                return

            self.action = self.action.child_primary(
                session=self.session)

            actions_counter += 1
        if reset_aggg_time:
            self.flow.aggregation_window_start_time = None

    def run_action(self):
        """

        For now this assumes children go in a line,
        ie it's not really a graph but that structure is there
        for future.

        Handles action level event

        """

        self.new_action_event()

        self.route_action()

    def complete_flow(self):
        """
        "complete" if there are no more children
        """

        self.flow_is_running = False

        # TODO update status of Flow Event?
        # May not be able to declare "success" but at least could declare "complete"

    def route_action(self):
        """

        Route to function based on action kind

        """

        # Use "simple" names till can think of more relevant ones.
        strategy_operations = {
            "file": self.file,
            "count": self.count,
            "condition": self.condition,
            "email": self.email,
            "webhook": self.webhook,
            "overlay": self.overlay
        }
        operation = strategy_operations.get(self.action.kind, None)
        if operation is None:
            self.log['error']['kind'] = "Invalid kind (No operation matches.)"
            return

        ### MAIN
        operation()

        ###

        if self.action_event.kind == "condition":

            # SQL alchemy is casting this as a bool
            # TODO update database to store as bool too

            # print(self.action_event.condition_result, type(self.action_event.condition_result))

            if self.action_event.condition_result == False:
                print("Condition is False, exiting")
                self.complete_flow()
                return

        if self.previous_action_event:
            # hacky
            self.previous_previous_action_event = self.previous_action_event

        self.previous_action_event = self.action_event


    def count(self):

        # Get inference from brain

        # Get label to check for

        # TODO merge operator with conditional

        # Handle counting based on class

        # TODO get from previous action

        inference = self.previous_action_event.brain_inference

        # Assumes label_dict as label_file_id

        label_dict = inference.ai.ml.label_dict

        # Defaults to storing our db id : model sequential number ie 121 : 1
        # Use this to convert model output to get actual labels
        inverted_label_file_dict = {v: k for k, v in label_dict.items()}

        # Why are we inverting it?

        # CAUTION the label dic is the label FILE
        # Class File not class Label here...
        # TODO clarify this better...

        image = inference.file.image

        counter = 0

        if inference.boxes['boxes']:

            # Caution, this expects boxes to be in a list
            # ie [ [0, 0, 0 ,0] ] even if only 1 box!!!!

            for i, box in enumerate(inference.boxes['boxes']):

                label = inference.classes['classes'][i]
                score = inference.scores['scores'][i]

                label_file_id = inverted_label_file_dict[label]

                # print(label, label_file_id, self.action.count_label_file_id)
                # print(type(label_file_id), type(self.action.count_label_file_id))

                if int(label_file_id) == (self.action.count_label_file_id):
                    counter += 1

                # Useful for minimum size in future

                # Denormalize cordinates

                y_min = int(round(box[0] * image.height))
                x_min = int(round(box[1] * image.width))
                y_max = int(round(box[2] * image.height))
                x_max = int(round(box[3] * image.width))

                width = x_max - x_min
                height = y_max - y_min

        # print(counter)

        # print(counter)
        self.action_event.count = counter

    # Get count operator / map to python operator
    conditional_operations = {
        "==": operator.eq,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "!=": operator.ne
    }

    def condition(self):

        OPERATOR = self.conditional_operations.get(
            self.action.condition_operator)

        # Compare new count to specificed count

        # TODO not sure how feel about casting as int
        # / how we we want to store that
        # should condition have a "type"?? or be some other type of
        # expression? then can store as string and cast as needed

        result = OPERATOR(
            self.previous_action_event.count,
            int(self.action.condition_right_operand))

        # Store result of operation in event
        self.action_event.condition_result = result

    # TODO also store previous count and operand?
    # ie for easier debugging

    # WIP WIP WIP
    def email(self):
        """


        """

        # Use Action specs
        # ie action.email_send_to

        # TODO what we want to send / put here...

        # Back two layers?
        # This feels pretty awkward!!! Also how we
        # want to construct this dynamically...
        logger.debug('[ActionFlow {}] Running Email Action'.format(self.flow.id))
        subject = "Diffgram Event"

        if self.previous_action_event:
            if self.previous_action_event.kind == "condition":
                count = self.previous_previous_action_event.count
                label = self.previous_previous_action_event.action.count_label_file.label

                subject = str(count) + " " + \
                          str(label.name) + " (s)"

        # TODO store url as more generic thing with flow event...

        url = "{}project/".format(settings.URL_BASE) + str(self.action.project.project_string_id) + \
              "/flow/" + str(self.flow.id) + "/event/" + str(self.flow_event.id)

        # Create Email Notification
        notification = Notification.new(
            session=self.session,
            channel_type='email',
            add_to_session=True,
            flush_session=True,
            type=self.trigger_event.type,
            task_id=self.trigger_event.task_id,
            job_id=self.trigger_event.job_id,
            input_id=self.trigger_event.input_id,
            member_created=self.trigger_event.member_created
        )

        if self.flow.time_window and hasattr(self.trigger_event, 'aggregation_window_start_time') and \
                self.trigger_event.aggregation_window_start_time:
            notification.send_email(session=self.session,
                                    email=self.action.email_send_to,
                                    start_time=self.trigger_event.aggregation_window_start_time)

        else:
            notification.send_email(session=self.session,
                                    email=self.action.email_send_to,
                                    start_time=None)

        self.action_event.email_was_sent_to = self.action.email_send_to

    def webhook(self):
        """


        """

        logger.debug('[ActionFlow {}] Running Webhook Action'.format(self.flow.id))

        # Create Email Notification
        # URL to flow
        url_webhook = self.action.url_to_post
        secret = self.action.secret_webhook

        notification = Notification.new(
            session=self.session,
            channel_type='webhook',
            add_to_session=True,
            flush_session=True,
            type=self.trigger_event.type,
            task_id=self.trigger_event.task_id,
            job_id=self.trigger_event.job_id,
            input_id=self.trigger_event.input_id,
            member_created=self.trigger_event.member_created
        )
        if self.flow.time_window and self.trigger_event.aggregation_window_start_time:
            notification.send_to_webhook(session=self.session,
                                         url=url_webhook,
                                         secret=secret,
                                         start_time=self.trigger_event.aggregation_window_start_time)

        else:
            notification.send_to_webhook(session=self.session, url=url_webhook, secret=secret)

    # Record Action event

    # Go to next

    def overlay(self):

        self.temp = tempfile.mkdtemp()

        inference = self.previous_action_event.brain_inference

        # Assumes label_dict as label_file_id

        label_dict = inference.ai.ml.label_dict

        # Defaults to storing our db id : model sequential number ie 121 : 1
        # Use this to convert model output to get actual labels
        inverted_label_file_dict = {v: k for k, v in label_dict.items()}

        # Class image() object
        image = inference.file.image

        if not inference.boxes['boxes']:
            return

        ## Now get the image and draw the overlay

        # Raw original image
        data_tools = Data_tools().data_tools

        image_string = data_tools.download_bytes(image.url_signed_blob_path)

        image_np = imread(BytesIO(image_string))

        # Convert to pill setup for drawing operations
        pil_image = PIL_Image.fromarray(image_np)

        # Get overlay image
        if self.action.overlay_kind == "image":
            overlay_string = data_tools.download_bytes(image.url_signed_blob_path)

            # Convert to numpy array
            overlay_blob_np = imread(BytesIO(overlay_string))

            pil_overlay_image = PIL_Image.fromarray(overlay_blob_np)

        # TODO optional "normal" box drawing

        # Caution, this expects boxes to be in a list
        # ie [ [0, 0, 0 ,0] ] even if only 1 box!!!!

        for i, box in enumerate(inference.boxes['boxes']):

            label = inference.classes['classes'][i]
            score = inference.scores['scores'][i]

            label_file_id = inverted_label_file_dict[label]

            # Pass on files that aren't equal to chosen label
            if int(label_file_id) != (self.action.overlay_label_file_id):
                continue

            # Denormalize cordinates

            y_min = int(round(box[0] * image.height))
            x_min = int(round(box[1] * image.width))
            y_max = int(round(box[2] * image.height))
            x_max = int(round(box[3] * image.width))

            width = x_max - x_min
            height = y_max - y_min

            center_x = int((x_max + x_min) / 2)
            center_y = int((y_max + y_min) / 2)

            # TODO condition on what kind of text / overlay we
            # are providing here.

            # TODO use cordinates and settings to position /
            # resize overlay as desired

            if self.action.overlay_kind == "image":
                # https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil

                pil_image.paste(
                    pil_overlay_image,
                    (center_x, center_y),
                    pil_overlay_image
                )

        # re upload updated / overlayed image

        image_out_filename = self.temp + "out.jpg"

        # Convert back from pill format
        image_np = np.array(pil_image)

        imwrite(image_out_filename, image_np)

        new_image = Image()
        self.session.add(new_image)

        new_image.url_signed_blob_path = "actions/completed" + \
                                         str(self.action_event.id) + "_out.jpg"

        self.action_event.overlay_rendered_image = new_image

        data_tools.upload_to_cloud_storage(image_out_filename,
                                           new_image.url_signed_blob_path,
                                           content_type = 'image/jpg')
