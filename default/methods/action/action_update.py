from methods.regular.regular_api import *  # Import regular_api methods

import re  # Regular expression module
from sqlalchemy.orm.session import Session  # SQLAlchemy session object
from shared.database.action.action import Action  # Action model
from shared.database.auth.member import Member  # Member model
from shared.database.action.workflow import Workflow  # Workflow model
from shared.database.action.action_template import Action_Template  # Action Template model
from shared.data_tools_core import Data_tools  # Data handling module

import tempfile  # Temporary file handling
import os  # Operating system module
from werkzeug.utils import secure_filename  # Secure file name handling
from shared.image_tools import imresize  # Image resizing
from imageio import imwrite  # Image writing
from flasgger import swag_from  # Swagger decorator
from shared.scheduler.job_scheduling import add_job_scheduling, remove_job_scheduling  # Job scheduling

@routes.route('/api/v1/project/<string:project_string_id>/actions/<int:action_id>', methods=['PUT'])
@Project_permissions.user_has_project(Roles=["admin", "Editor"], apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
@swag_from('../../docs/actions/action_update.yml')
def api_action_update(project_string_id, action_id):
    """
    Update an action in a project.

    Parameters:
    project_string_id (string): The unique identifier of the project.
    action_id (int): The unique identifier of the action.

    The request should contain a JSON payload with the updated action details.

    Returns:
    A JSON response containing the updated action and log information.
    """
    spec_list = [
        # ... (spec_list definition)
    ]

    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        member = get_member(session)
        project = Project.get(session, project_string_id)

        result, log = action_update_core(
            session=session,
            project=project,
            member=member,
            public_name=input['public_name'],
            action_id=action_id,
            kind=input['kind'],
            description=input['description'],
            trigger_data=input['trigger_data'],
            config_data=input['config_data'],
            template_id=input['template_id'],
            completion_condition_data=input['completion_condition_data'],
            workflow_id=input['workflow_id'],
            ordinal=input['ordinal'],
            archived=input['archived'],
            icon=input['icon'],
            output_interface=input['output_interface'],
            precondition=input['precondition'],
            log=log,
        )

        # For init errors
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400
        #
        out = jsonify(action=result, log=log)
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
                       template_id: int,
                       workflow_id: int,
                       ordinal: int,
                       archived: bool,
                       completion_condition_data: dict,
                       log: dict,
                       output_interface: dict,
                       precondition
                       ):
    """
    Core function to update an action in the database.

    Parameters:
    session (Session): SQLAlchemy session object.
    project (Project): The project object.
    member (Member): The member object.
    public_name (str): The updated public name of the action.
    action_id (int): The unique identifier of the action.
    icon (str): The updated icon of the action.
    kind (str): The updated kind of the action.
    description (str): The updated description of the action.
    trigger_data (dict): The updated trigger data of the action.
    config_data (dict): The updated config data of the action.
    template_id (int): The updated template ID of the action.
    workflow_id (int): The updated workflow ID of the action.
    ordinal (int): The updated ordinal of the action.
    archived (bool): The updated archived status of the action.
    completion_condition_data (dict): The updated completion condition data of the action.
    log (dict): The log dictionary.
    output_interface (dict): The updated output interface of the action.
    precondition (dict): The updated precondition of the action.

    Returns:
    A tuple containing the updated action and the log dictionary.
    """
    workflow = Workflow.get_by_id(session=session, id=workflow_id, project_id=project.id)
    if workflow is None:
        log['error']['workflow'] = f'Workflow id {workflow_id} not found'
        return False, log

    action_template = Action_Template.get_by_id(session=session, id=template_id)
    if action_template is None:
        log['error']['action_template'] = f'Action template id {template_id} not found'
        return False, log

    action = Action.get_by_id(session=session, id=action_id, project_id=project.id)
    if action is None:
        log['error']['action'] = f'Action {action_id} not found in project {project.project_string_id}'
    previous_trigger_data = action.trigger_data.copy()
    data_to_update = {
        # ... (data_to_update definition)
    }
    for key, val in data_to_update.items():
        setattr(action, key, val)
    # ... (Update Scheduler if first action and time schedule set)
    session.add(action)
    res = action.serialize()

    return res, log


# ... (Other functions)

@routes.route('/api/v1/project/<string:project_string_id>' + '/action/overlay/image', methods=['POST'])
@Project_permissions.user_has_project(Roles=["admin", "Editor"], apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("3 per day")
def update_overlay_image_api(project_string_id):
    """
    Update the overlay image for an action in a project.

    Parameters:
    project_string_id (string): The unique identifier of the project.

    The request should contain a file with the overlay image.

    Returns:
    A JSON response containing success information and the updated action.
    """
    file = request.files.get('file')
    if not file:
        return "No file", 400

    # ... (File handling and validation)

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        action = Action.get_by_id(
            session=session,
            id=action_id,
            project_id=project.id)

        # ... (Process and save the image)

        session.add(action)

        return jsonify(success=True, action=action.serialize()), 200


def process_image_for_overlay(
        session,
        file,
        file_name,
        content_type,
        blob_base,
        extension):
    """
    Process and save an image for overlay.

    Parameters:
    session (Session): SQLAlchemy session object.
    file (FileStorage): The file object.
    file_name (string): The name of the file.
    content_type (string): The content type of the file.
    blob_base (string): The base path for the blob.
    extension (string): The extension of the file.

    Returns:
    The updated Image object.
    """

    # ... (Image processing and saving)

    return new_image
