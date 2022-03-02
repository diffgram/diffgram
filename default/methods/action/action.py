from methods.regular.regular_api import *

import re

from shared.database.action.action import Action
from shared.database.action.action_flow import Action_Flow
from shared.database.action.action_template import Action_Template
from shared.data_tools_core import Data_tools

import tempfile
import os
from werkzeug.utils import secure_filename
from shared.image_tools import imresize
from imageio import imwrite


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/single',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_update_or_new(project_string_id):
    """
    Shared route for update and new

    """

    spec_list = [
        {'action': dict},
        {'mode': str}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        # Caution, declaring as user.member for now.
        member = user.member

        action_session = Action_Session(
            session=session,
            member=member,
            project=project,
            org=project.org,
            log=log,
            action_dict=input['action'],
            mode=input['mode']
        )

        # For init errors
        if len(action_session.log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        if action_session.mode in ["UPDATE", "ARCHIVE"]:

            action_session.update_mode_init()

            if len(action_session.log["error"].keys()) >= 1:
                return jsonify(log=log), 400

        action_session.route_kind_using_strategy_pattern()

        log = action_session.log
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        action = action_session.action
        log['success'] = True

        if action_session.mode == "NEW":
            # Just putting it here for now while
            # Figuring out how we are loading member
            # Probably could be in action_session()
            Event.new(
                session=session,
                kind="new_action",
                member=member,
                success=True,
                project_id=project.id,
                email=user.email
            )

        out = jsonify(action=action.serialize(),
                      log=log)
        return out, 200


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

valid_next_actions = {
    'init': ["email", "webhook"],
    'count': ["condition", "email"],
    'condition': ["email"],
    'overlay': ["email"]
}


def validate_email(email):
    if email and EMAIL_RE.match(email):
        return True
    else:
        return False


class Action_Session():
    """
    Holding class so we don't have to keep calling
    session and project for each function
    """

    def __init__(
            self,
            session,
            member,
            project,
            org,
            log,
            action_dict,
            mode
    ):

        self.session = session
        self.member = member
        self.project = project
        self.mode = mode
        self.log = log

        # Key point, action_dict is the UNTRUSTED dictionary input
        # Where as action is class Action object in our system as it gets created
        self.action_dict = action_dict
        self.mode = mode
        ####

        self.org = org
        self.action = None

        # Declared before action is created,
        # after we call action.kind
        # Kind is not checked at init since it's handled as part of
        # route_kind_using_strategy_pattern()
        self.kind = None
        self.flow = None

        # FUNCTIONS
        self.verify_and_set_flow_id()

    def update_mode_init(self):

        self.action = Action.get_by_id(
            session=self.session,
            id=self.action_dict.get('id'),
            project_id=self.project.id)

        if self.action is None:
            log['error']['action'] = "No Action found"
            return

        # TODO check self.mode in allowed modes?

        # Default archive case
        if self.mode == 'ARCHIVE':

            self.session.add(self.action)
            self.action.archived = True
            self.action.active = False

            if self.flow.first_action_id == self.action.id:

                self.flow.first_action_id = None
                self.session.add(self.flow)

            else:

                # TODO handle reseting links for children
                # and parents?

                pass

            # WIP WIP WIP
            # NOT WORKING CODE
            # if self.action.child_primary_id:

        # self.action.child_primary

        # self.action.parent_id

    def verify_and_set_flow_id(self):
        """
        We could also expect the flow id as part of request but
        it feels "cleaner"? to have it as part of action_dict.
        Only real difference is this extra check instead of defining in intial
        spec_list.

        Also for front end then we can assign it as a computed property,
        and it's the "same" for various setups. (ie casting as Number() ) etc.

        Expects self.action_dict to exist
        """

        flow_id = self.action_dict.get('flow_id', None)
        if flow_id is None:
            self.log['error']['flow_id'] = "Invalid flow_id (None provided.)"
            return

        # Careful can't assign this directly to action yet (as it may not exist)
        self.flow = Action_Flow.get_by_id(
            session=self.session,
            id=flow_id,
            project_id=self.project.id)

        if self.flow is None:
            self.log['error']['flow'] = "Invalid flow (Does not match project or bad id)."
            return

        if self.flow.is_new is True:
            self.session.add(self.flow)
            self.flow.is_new = False

    def route_kind_using_strategy_pattern(self):
        """

        Route to function based on action kind

        Similar to when actually running an action
        But here for managing creation

        """

        self.kind = self.action_dict.get('kind', None)
        if self.kind is None:
            self.log['error']['kind'] = "Invalid kind (None provided.)"
            return

        # Use "simple" names till can think of more relevant ones.
        strategy_operations = {
            "count": self.count,
            "condition": self.condition,
            "delay": self.delay,
            "email": self.email,
            "webhook": self.webhook,
            "overlay": self.overlay
        }

        operation = strategy_operations.get(self.kind, None)

        if operation is None:
            self.log['error']['kind'] = "Invalid kind (No operation matches.) Kind was:" + \
                                        str(self.kind)
            return

        self.template = Action_Template.get_by_kind(
            kind=self.kind,
            session=self.session)

        if self.template is None:
            self.log['error']['kind'] = "Invalid template (Doesn't exist.)"
            return

        # Only check constraints on new?
        if self.mode == 'NEW':
            constraints_result = self.constraints()
            if constraints_result is False:
                self.log['error']['constraint'] = "Invalid next action."
                return
        operation()

    def condition(self):

        if self.mode == "ARCHIVE":
            return

        if self.mode == "NEW":
            self.new_action()

        if self.mode == "UPDATE":
            # Special logic for update if required.
            pass

        spec_list = [
            {'right_operand': int},
            {'operator': str}]

        self.log, input = regular_input.input_check_many(
            spec_list=spec_list,
            log=self.log,
            untrusted_input=self.action_dict.get('condition', None))

        if len(self.log["error"].keys()) >= 1:
            return

        # "count" or "condition_right_operand"?

        # Careful, action is a "flat" class condition_operator
        # not condition.operator

        self.action.condition_right_operand = input['right_operand']

        if self.action.condition_right_operand < 0 or \
                self.action.condition_right_operand > 100:
            self.log['error']['condition']['count'] = "Count must be between 0 and 100"
            return

        self.action.condition_operator = input['operator']
        valid_operator_list = ['==', '>', '>=', '<', '<=', '!=']

        if self.action.condition_operator not in valid_operator_list:
            self.log['error']['operator'] = str(self.action.condition_operator) + \
                                            " is not a valid operator."
            return

        self.success()

    def constraints(self):
        """
        requires flow to be set
        and kind
        """

        valid = None

        if not self.flow.first_action_id:

            valid = valid_next_actions['init']

        else:

            parent_kind = self.flow.last_action.kind

            valid = valid_next_actions.get(parent_kind, None)

        # Valid could also be None if say .get() operation fails
        if valid is None:
            return False

        if self.kind is None or self.kind not in valid:
            return False

    def success(self):

        self.session.add(self.action)
        self.session.flush()

        self.session.add(self.flow)

        # Relationships

        # For now, naively assume that the "last" action
        # is the parent. (ie that actions are added in order)

        # Only update on New for now?

        if self.mode == 'NEW':

            if self.flow.first_action_id:

                # set ids directly to avoid issues with
                # sql alchemy

                self.flow.last_action.child_primary_id = self.action.id

                self.action.parent_id = self.flow.last_action.id

                self.flow.last_action_id = self.action.id

            else:

                self.flow.first_action_id = self.action.id
                self.flow.last_action_id = self.action.id

    def delay(self):

        pass

    # WIP WIP WIP


    def count(self):

        if self.mode == "ARCHIVE":
            return

        if self.mode == "NEW":
            self.new_action()

        if self.mode == "UPDATE":
            # Special logic for update if required.
            pass

        spec_list = [
            {'label_file_id': int}]

        self.log, input = regular_input.input_check_many(
            spec_list=spec_list,
            log=self.log,
            untrusted_input=self.action_dict.get('count', None))

        if len(self.log["error"].keys()) >= 1:
            return jsonify(log=self.log), 400

        # TODO validate correct label file

        label_file_id = input['label_file_id']

        # None's as workaround since function expects it
        existing_file = File.get_by_id_untrusted(
            session=self.session,
            user_id=None,
            project_string_id=None,
            file_id=label_file_id,
            directory_id=self.project.directory_default_id)

        # Declare as part of dict?
        # ie
        self.action.count_label_file = existing_file

        if self.action.count_label_file is None:
            self.log['error']['label_file'] = str(label_file_id) + \
                                              " label_file_id is not valid."
            return

        self.success()

    def email(self):

        if self.mode == "ARCHIVE":
            return

        if self.mode == "NEW":
            self.new_action()

        if self.mode == "UPDATE":
            pass

        spec_list = [
            {'email_send_to': str}]

        self.log, input = regular_input.input_check_many(
            spec_list=spec_list,
            log=self.log,
            untrusted_input=self.action_dict.get('email', None))

        if len(self.log["error"].keys()) >= 1:
            return jsonify(log=self.log), 400

        self.action.email_send_to = input['email_send_to']

        valid_email = validate_email(self.action.email_send_to)
        if not valid_email:
            self.log['error']['email'] = "Invalid email"
            return jsonify(log=self.log), 400

        self.success()

    def webhook(self):

        if self.mode == "ARCHIVE":
            return

        if self.mode == "NEW":
            self.new_action()

        if self.mode == "UPDATE":
            pass

        spec_list = [
            {'url_to_post': str},
            {'secret_webhook': str}
        ]
        self.log, input = regular_input.input_check_many(
            spec_list=spec_list,
            log=self.log,
            untrusted_input=self.action_dict.get('webhook', None))

        if len(self.log["error"].keys()) >= 1:
            return jsonify(log=self.log), 400

        self.action.url_to_post = input['url_to_post']
        self.action.secret_webhook = input['secret_webhook']

        self.success()

    def overlay(self):

        if self.mode == "ARCHIVE":
            return

        if self.mode == "NEW":
            self.new_action()

        if self.mode == "UPDATE":
            pass

        spec_list = [
            {'label_file_id': int}]

        # TODO would be nice for say "overlay"
        # to be the "kind" or something" then don't have to change for
        # each
        self.log, input = regular_input.input_check_many(
            spec_list=spec_list,
            log=self.log,
            untrusted_input=self.action_dict.get('overlay', None))

        if len(self.log["error"].keys()) >= 1:
            return jsonify(log=self.log), 400

        # DEFAULT this to image for now
        self.action.overlay_kind = "image"

        # TODO maybe share with count?

        label_file_id = input['label_file_id']

        # None's as workaround since function expects it
        existing_file = File.get_by_id_untrusted(
            session=self.session,
            user_id=None,
            project_string_id=None,
            file_id=label_file_id,
            directory_id=self.project.directory_default_id)

        self.action.overlay_label_file = existing_file

        if self.action.overlay_label_file is None:
            self.log['error']['label_file'] = str(label_file_id) + \
                                              " label_file_id is not valid."
            return

        self.success()

    def new_action(self):
        """
        Standard new_action() to be used in part
        with Action_Session() and the route_kind_using_strategy_pattern()
        patterns. Share amoung various kinds that all create new().

        To consider, we could call this at start of route strategy
        or similar, based on mode BUT downside is that
        we may not want to actually create the action until
        we have verified the info needed is correct.

        We only want do add the action if no errors

        """

        self.action = Action.new(
            session=self.session,
            project=self.project,
            kind=self.kind,
            org=self.org,
            member=self.member,
            flow=self.flow,
            template=self.template
        )


images_allowed_file_names = [".jpg", ".jpeg", ".png"]


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/overlay/image',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("3 per day")
def update_overlay_image_api(project_string_id):
    file = request.files.get('file')
    if not file:
        return "No file", 400

    extension = os.path.splitext(file.filename)[1].lower()
    if extension in images_allowed_file_names:

        file.filename = secure_filename(
            file.filename)  # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        temp_dir = tempfile.mkdtemp()
        file_name = temp_dir + "/" + file.filename
        file.save(file_name)

        action_id = request.headers['action_id']
        if action_id is None:
            return "error no action_id", 400

        with sessionMaker.session_scope() as session:

            project = Project.get(session, project_string_id)

            action = Action.get_by_id(
                session=session,
                id=action_id,
                project_id=project.id)

            with open(file_name, "rb") as file:
                content_type = "image/" + str(extension)
                short_file_name = os.path.split(file_name)[1]

                action.overlay_image = process_image_for_overlay(
                    session=session,
                    file=file,
                    file_name=short_file_name,
                    blob_base="actions/overlay_images/",
                    content_type=content_type,
                    extension=extension)

                session.add(action)

            return jsonify(success=True,
                           action=action.serialize()), 200

    return jsonify(success=False), 400


from shared.database.image import Image
from imageio import imread
import shutil


# TODO merge with process media?
# I don't want to jump to using that because so much of it based on Input class
# And not clear if we want that for something like this
# Maybe we do...

def process_image_for_overlay(
        session,
        file,
        file_name,
        content_type,
        blob_base,
        extension):
    """

    In comparison to other methods we want to
     * Keep PNG transparency

        session, db session object
        file, python file pointer???
        file_name, string?
        content_type, string??
        blob_base, string, ie "projects/images/" must end with "/" slash
        extension, ?? must include "."?

    """

    new_image = Image(original_filename=file_name)
    session.add(new_image)

    try:
        session.commit()
    except:
        session.rollback()
        raise

    image_blob = blob_base + str(new_image.id)
    image_blob_thumb = image_blob + "_thumb"


    image = imread(file)

    if image is None:
        raise IOError("Could not open")

    new_image.height = image.shape[0]
    new_image.width = image.shape[1]

    if image.shape[0] > 640 or image.shape[1] > 640:
        ratio = min((640 / image.shape[0]),
                    (640 / image.shape[1]))

        shape_x = int(round(image.shape[0] * ratio))
        shape_y = int(round(image.shape[1] * ratio))

        image = imresize(image,
                                    (shape_x, shape_y))

    # Save File
    temp = tempfile.mkdtemp()
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, image)
    new_image.height = image.shape[0]
    new_image.width = image.shape[1]

    data_tools = Data_tools().data_tools

    data_tools.upload_to_cloud_storage(temp_local_path = new_temp_filename,
                                       blob_path = image_blob,
                                       content_type = "image/" + str(extension))

    signed_url = data_tools.build_secure_url(blob_name = image_blob, expiration_offset = 45920000)

    # Save Thumb
    thumbnail_image = imresize(image, (80, 80))
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, thumbnail_image)

    data_tools.upload_to_cloud_storage(temp_local_path = new_temp_filename,
                                       blob_path = image_blob_thumb,
                                       content_type = "image/" + str(extension))

    signed_url_thumb = data_tools.build_secure_url(blob_name = image_blob_thumb, expiration_offset = 45920000)

    session.add(new_image)

    shutil.rmtree(temp)  # delete directory

    # Two different generations of naming conventions... todo review
    new_image.url_signed = signed_url
    new_image.url_signed_blob_path = image_blob

    new_image.url_signed_thumb = signed_url_thumb
    new_image.url_signed_thumb_blob_path = image_blob_thumb

    new_image.url_signed_expiry = int(time.time() + 45920000)

    return new_image
