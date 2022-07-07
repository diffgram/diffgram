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


@routes.route('/api/v1/project/<string:project_string_id>/actions/<int:action_id>',
              methods = ['PUT'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_update(project_string_id, action_id):
    """

    """

    spec_list = [
        {'public_name': str},
        {'kind': str},
        {'icon': str},
        {'config_data': dict},
        {'description': str},
        {'template_id': int},
        {'workflow_id': int},
        {'ordinal': int},
        {'archived': bool},
        {'condition_data': 
            {
            'default': None,
            'kind': dict
            }
        },
        {'trigger_data': 
            {
            'default': None,
            'kind': dict
            }
        },
        {'completion_condition_data': 
            {
            'default': None,
            'kind': dict
            }
        },
        {
            'output_interface': {
                'default': None,
                'kind': dict
            }
        }

    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        member = get_member(session)
        project = Project.get(session, project_string_id)

        result, log = action_update_core(
            session = session,
            project = project,
            member = member,
            public_name = input['public_name'],
            action_id = action_id,
            kind = input['kind'],
            description = input['description'],
            trigger_data = input['trigger_data'],
            condition_data = input['condition_data'],
            config_data = input['config_data'],
            template_id = input['template_id'],
            completion_condition_data = input['completion_condition_data'],
            workflow_id = input['workflow_id'],
            ordinal = input['ordinal'],
            archived = input['archived'],
            icon = input['icon'],
            output_interface = input['output_interface'],
            log = log,
        )

        # For init errors
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        #
        out = jsonify(action = result,
                      log = log)
        return out, 200


def action_update_core(session: Session,
                       project: Project,
                       member: Member,
                       public_name: str,
                       action_id: int,
                       icon: str,
                       kind: str,
                       description: str,
                       trigger_data: dict,
                       config_data: dict,
                       condition_data: dict,
                       template_id: int,
                       workflow_id: int,
                       ordinal: int,
                       archived: bool,
                       completion_condition_data: dict,
                       log: dict,
                       output_interface: dict
                       ):
    workflow = Workflow.get_by_id(session = session, id = workflow_id, project_id = project.id)
    if workflow is None:
        log['error']['workflow'] = f'Workflow id {workflow_id} not found'
        return False, log

    action_template = Action_Template.get_by_id(session = session, id = template_id)
    if action_template is None:
        log['error']['action_template'] = f'Action template id {action_template_id} not found'
        return False, log

    action = Action.get_by_id(session = session, id = action_id, project_id = project.id)
    if action is None:
        log['error']['action'] = f'Action {action_id} not found in project {project.project_string_id}'
    data_to_update = {
        'public_name': public_name,
        'action_id': action_id,
        'icon': icon,
        'kind': kind,
        'description': description,
        'trigger_data': trigger_data,
        'config_data': config_data,
        'condition_data': condition_data,
        'template_id': template_id,
        'workflow_id': workflow_id,
        'ordinal': ordinal,
        'archived': archived,
        'completion_condition_data': completion_condition_data,
        'member_updated_id': member.id,
        'output_interface': output_interface
    }
    for key, val in data_to_update.items():
        setattr(action, key, val)

    session.add(action)
    res = action.serialize()

    return res, log


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
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
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
                session = session,
                id = action_id,
                project_id = project.id)

            with open(file_name, "rb") as file:
                content_type = "image/" + str(extension)
                short_file_name = os.path.split(file_name)[1]

                action.overlay_image = process_image_for_overlay(
                    session = session,
                    file = file,
                    file_name = short_file_name,
                    blob_base = "actions/overlay_images/",
                    content_type = content_type,
                    extension = extension)

                session.add(action)

            return jsonify(success = True,
                           action = action.serialize()), 200

    return jsonify(success = False), 400


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

    new_image = Image(original_filename = file_name)
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
