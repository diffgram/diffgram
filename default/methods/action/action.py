from methods.regular.regular_api import *

import re
from sqlalchemy.orm.session import Session
from shared.database.action.action import Action
from shared.database.auth.member import Member
from shared.database.action.workflow import Workflow
from shared.database.action.action_template import Action_Template
from shared.data_tools_core import Data_tools

import tempfile
import os
from werkzeug.utils import secure_filename
from shared.image_tools import imresize
from imageio import imwrite


@routes.route('/api/v1/project/<string:project_string_id>/actions/workflow/<int:project_string_id>/action/new',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_new(project_string_id):
    """
    Shared route for update and new

    """

    spec_list = [
        {'name': dict},
        {'trigger_data': dict},
        {'description': str},
        {'complete_condition': str},
        {'action_template_id': int},
        {'condition_data': str}

    ]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        # Caution, declaring as user.member for now.
        member = user.member
        action_creation_core(
            session = session,
            project = project,
            member = member,
            name = input['name'],
            description = input['description'],
            trigger_data = input['trigger_data'],
            condition_data = input['condition_data'],
            action_template_id = input['action_template_id'],
            complete_condition = input['complete_condition'],
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


def action_creation_core(session: Session,
                         project: Project,
                         member: Member,
                         name: str,
                         description: str,
                         trigger_data: str,
                         condition_data: dict,
                         action_template_id: int,
                         complete_condition: str):


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
