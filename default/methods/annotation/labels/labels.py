# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

from google.cloud import storage

from shared.database.user import UserbaseProject
from shared.database.image import Image
from shared.database.annotation.instance import Instance
from shared.database.label import Label

from shared.database.video.sequence import Sequence
from shared.database.video.video import Video

from shared.helpers.permissions import getUserID
from shared.helpers.permissions import get_gcs_service_account

from shared.database.source_control.working_dir import WorkingDirFileLink


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/label/new',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_label_new(project_string_id):
    """
    Input a single label

    """

    spec_list = [
        {'name': str},
        {'colour': None},
        {"default_sequences_to_single_frame": {
            'default': False,
            'kind': bool
        }
        }
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        label_file = new_label_file_object_core(session, input, project_string_id, log)

        if not label_file:
            return jsonify(log = log), 400

        return jsonify(log = log, label = label_file.serialize()), 200


def new_label_file_object_core(session, input, project_string_id, log):
    """
    Creates Label File specific to this project
    """
    project = Project.get_project(session, project_string_id)

    colour = input['colour']

    if not colour:
        colour = default_color()

    project = Project.get(session, project_string_id)

    label_file = File.new_label_file(
        session=session,
        name=input['name'],
        default_sequences_to_single_frame=input['default_sequences_to_single_frame'],
        working_dir_id=project.directory_default_id,
        project=project,
        colour=colour,
        log=log,
    )

    if not label_file:
        return None

    member = get_member(session = session)

    Event.new(
        session = session,
        kind = "new_label",
        member = member,
        success = True,
        project_id = project.id
    )

    log['success'] = True

    return label_file


# Rename labels view?

@routes.route('/api/project/<string:project_string_id>' +
              '/labels/refresh',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def labelRefresh(project_string_id):
    """
    Get labels from project

    In future we could get this from a provided directory,
    but for now labels all rest in project default directory

    In the past we got this from a individual user's directory but that doesn't
    make sense in new context Of projects knowing all their directories,
    sharing work, and even simply using API keys instead of just users logging in

    """

    # TODO pull different labels from different places depending on project
    # Here is in context of a user editing...
    # Need to know what branch / version...
    # ie to get from project's master branch
    # version = project.master_branch.latest_version

    with sessionMaker.session_scope() as session:

        project = Project.get_project(session, project_string_id)
        directory = project.directory_default

        labels_out = project.get_label_list(session, directory = directory)
        # Assume can't easily sort this in sql because it's the label which is one layer below
        # labels_out.sort(key=lambda x: x['label']['name'])

        return jsonify(labels_out = labels_out,
                       label_file_colour_map = directory.label_file_colour_map), 200


@routes.route('/api/project/<string:project_string_id>' +
              '/labels/colour_map',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer"])
def label_colour_map(project_string_id):
    """

    """

    if project_string_id is None:
        return "no project id", 400

    with sessionMaker.session_scope() as session:

        project = Project.get_project(session, project_string_id)
        if project is None:
            return json.dumps("Error"), 400, {'ContentType': 'application/json'}

        directory = project.directory_default

        return jsonify(success = True,
                       label_file_colour_map = directory.label_file_colour_map), 200



@routes.route('/api/project/<string:project_string_id>/labels/edit',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def label_edit(project_string_id):
    with sessionMaker.session_scope() as session:

        data = request.get_json(force = True)  # Force = true if not set as application/json'
        label_file = data.get('label_file', None)

        if label_file is None:
            return json.dumps("file is None"), 400, {'ContentType': 'application/json'}

        label_proposed = label_file.get('label', None)
        if label_proposed is None:
            return json.dumps("label is None"), 400, {'ContentType': 'application/json'}

        name_proposed = label_proposed.get('name', None)
        if name_proposed is None or len(name_proposed) < 1:
            return json.dumps("label less than 1 character"), 400, {'ContentType': 'application/json'}

        label_file_id = label_file.get('id', None)
        if label_file_id is None:
            return json.dumps("no label id"), 400, {'ContentType': 'application/json'}

        # WIP...
        user_id = getUserID()

        existing_file = File.get_by_id_untrusted(session,
                                                 user_id,
                                                 project_string_id,
                                                 label_file_id)

        if existing_file is None:
            return jsonify("No file"), 400

        if existing_file.committed is True:
            return jsonify("File committed"), 400

            # TODO # WIP WIP
            new_file = File.copy_file_from_existing(
                session,
                working_dir,
                existing_file)


            label_file = File.new_label_file(
                session = session,
                name = name_proposed,
                default_sequences_to_single_frame = None,
                working_dir_id = project.directory_default_id,
                project = project,
                colour = colour_proposed,
                log = log,
                existing_file=new_file
            )
        # WIP

        if existing_file.committed is not True:

            project = Project.get(session, project_string_id)

            user = session.query(User).filter(User.id == user_id).one()
            working_dir = project.directory_default

            colour_proposed = label_file.get("colour", None)

            # Caution note, 'label_proposed' not file
            default_sequences_to_single_frame_proposed = label_proposed.get(
                "default_sequences_to_single_frame")

            if default_sequences_to_single_frame_proposed is None:
                default_sequences_to_single_frame_proposed = False

            # Caution
            # We need this because we are trying to
            # maintain unique labels...
            # It's the Label() class we are getting not the File()
            # (Which we already have).
            label = Label.new(
                session,
                name=name_proposed,
                default_sequences_to_single_frame=default_sequences_to_single_frame_proposed)

            existing_file.label_id = label.id
            existing_file.colour = colour_proposed

            session.add(existing_file)

            working_dir.label_file_colour_map[existing_file.id] = colour_proposed
            # Caution: https://stackoverflow.com/questions/42559434/updates-to-json-field-dont-persist-to-db
            flag_modified(working_dir, "label_file_colour_map")
            # This seems to be needed to reliably detect changes
            # Maybe didn't need it prior as was editing sub "lists" vs editing ID directly
            # This still feels better than passing whole item to python memory and editing it
            # (Which still also doesn't always work as expected.)

            session.add(working_dir)
        # return existing_file

        """

        Option 1
        Create new files for a label change
        ie get all file attached to the label
        Create a new file for every one, and attach it to that new label
        Then any future changes to label don't have to create new files
        Till it's comitted
        Then would whave to create new ones again

        ie Instance.label_id == 

        """

        out = 'success'
        return json.dumps(out), 200, {'ContentType': 'application/json'}


def migrate():
    with sessionMaker.session_scope() as session:
        existing_label_file_list = session.query(File).filter(File.type == "label").all()

        # Good but was missing a not none check!

        for file in existing_label_file_list:
            file.colour = file.label.colour
            session.add(file)


def merge():
    instance_list = []  # TODO get instances across project

    label_file_to_change_to = 1  # ids
    label_file_to_eligible_merge_list = []  # ids

    # a few other considerations

    for instance in instance_list:

        if instance.label_file_id in label_file_to_eligible_merge_list:
            pass

            # handle if committed
            # update hash...

            instance.label_file_id = label_file_to_change_to
            session.add(instance)


def default_color():
    return {
        "a": 1,
        "hex": "#00FF80",
        "hsl": {
            "a": 1,
            "h": 150,
            "l": 0.5,
            "s": 1
        },
        "hsv": {
            "a": 1,
            "h": 150,
            "s": 1,
            "v": 1
        },
        "oldHue": 150,
        "rgba": {
            "a": 1,
            "b": 128,
            "g": 255,
            "r": 0
        },
        "source": "hsva"
    }
