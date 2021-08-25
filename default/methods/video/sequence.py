# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    print("can't import regular api (sequence.py)")

from google.resumable_media.requests import ResumableUpload

from shared.database.image import Image
from shared.database.annotation.instance import Instance
from shared.helpers.permissions import getUserID
from shared.database.user import UserbaseProject

from shared.database.video.video import Video
from shared.database.video.sequence import Sequence
from sqlalchemy.orm import joinedload
import threading
import traceback


@routes.route('/api/project/<string:project_string_id>' +
              '/video/single/<int:video_file_id>' +
              '/sequence/list',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def get_sequence(project_string_id, video_file_id):
    start_time = time.time()
    with sessionMaker.session_scope() as session:
        # careful FILE id not raw video_id

        sequence_list = session.query(Sequence).options(joinedload(Sequence.label_file)).filter(
            Sequence.video_file_id == video_file_id).all()

        # This is more to get key frames or?
        sequence_list_serialized = []

        for sequence in sequence_list:
            sequence_list_serialized.append(sequence.serialize())

        out = jsonify(success = True,
                      sequence_list = sequence_list_serialized)

        end_time = time.time()
        print("", end_time - start_time)
        return out, 200, {'ContentType': 'application/json'}


@routes.route('/api/v1/task/<int:task_id>'
              '/video/file_from_task'
              '/label/<int:label_file_id>'
              '/sequence/list',
              methods = ['GET'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def get_sequence_from_label_using_task(task_id, label_file_id):
    with sessionMaker.session_scope() as session:
        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        project = task.project

        return get_sequence_from_label_shared(
            session, task.file_id, label_file_id)


@routes.route('/api/project/<string:project_string_id>' +
              '/video/single/<int:video_file_id>' +
              '/label/<int:label_file_id>'
              '/sequence/list',
              methods = ['GET'])
@Project_permissions.user_has_project(["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def get_sequence_from_label(project_string_id, video_file_id, label_file_id):
    with sessionMaker.session_scope() as session:
        return get_sequence_from_label_shared(
            session, video_file_id, label_file_id)


def get_sequence_from_label_shared(session, video_file_id, label_file_id):
    if label_file_id is None or video_file_id is None:
        return "a required argument is none", 400, {'ContentType': 'application/json'}

    sequence_list_serialized = []

    sequence_list = session.query(Sequence).filter(
        Sequence.video_file_id == video_file_id,
        Sequence.label_file_id == label_file_id,
        Sequence.archived == False).order_by(
        Sequence.number).limit(250).all()

    # When we save a new sequence we don't check every existing one
    # So when we do this, we store highest sequence number
    # Could cache this...

    highest_sequence_number = 0
    for sequence in sequence_list:
        serialized = sequence.serialize_for_label_subset(
            session = session)
        sequence_list_serialized.append(serialized)

        if sequence.number > highest_sequence_number:
            highest_sequence_number = sequence.number

    return jsonify(success = True,
                   sequence_list = sequence_list_serialized,
                   highest_sequence_number = highest_sequence_number), 200


@routes.route('/api/project/<string:project_string_id>' +
              '/video/single/<int:video_file_id>' +
              '/label/<int:label_file_id>'
              '/sequence/<int:sequence_id>'
              '/remove',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def delete_sequence(
    project_string_id,
    video_file_id,
    label_file_id,
    sequence_id):
    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)

        file = File.get_by_id_and_project(
            session = session,
            project_id = project.id,
            file_id = video_file_id)

        if file is None: return "error security check if file access file failed"

        return delete_sequence_shared(session, file, label_file_id, sequence_id)


@routes.route('/api/v1/task/<int:task_id>'
              '/video/file_from_task'
              '/label/<int:label_file_id>'
              '/sequence/<int:sequence_id>'
              '/remove',
              methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def delete_sequence_using_task_id(task_id, label_file_id, sequence_id):
    with sessionMaker.session_scope() as session:
        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        # TODO handle if task is None

        return delete_sequence_shared(session, task.file, label_file_id, sequence_id)


def delete_sequence_shared(session, file, label_file_id, sequence_id):
    """
    We don't want to hard delete a sequence because it can cause
    foreign key issues. ie the instance sticks around or relates to the id,
        it then attempts to save it, but the sequence doesnt' exist
        also if we want todo recovery things in the future this could have issues too...

    """

    if label_file_id is None or sequence_id is None:
        return "a required argument is none", 400, {'ContentType': 'application/json'}

    # There are multiple sequences per video and per label, so need ID too
    # Could of course just do by ID but feels like an extra "check" that other stuff matches too

    sequence = session.query(Sequence).filter(
        Sequence.video_file_id == file.id,
        Sequence.label_file_id == label_file_id,
        Sequence.id == sequence_id).first()

    if sequence is None:
        return jsonify("Not found"), 400

    for instance in sequence.instance_list:
        instance.do_soft_delete()
        session.add(instance)

    sequence.archived = True
    session.add(sequence)

    return jsonify(success = True), 200


#### UPDATE
"""
We need the file or project for permissions
(ie to confirm the file id matches the sequence id
when we go to get it)

TODO consider having "remove" use some of shared update concepts

This is somewhat generic but was orginally built in context of 
label file updates.

"""
update_sequence_spec_list = [
    {"mode": str},
    {"payload": {
        'kind': dict
    }
    }]


@routes.route('/api/project/<string:project_string_id>' +
              '/video/single/<int:video_file_id>' +
              '/sequence/<int:sequence_id>'
              '/update',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def update_sequence(
    project_string_id,
    video_file_id,
    sequence_id):
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = update_sequence_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        file = File.get_by_id_and_project(
            session = session,
            project_id = project.id,
            file_id = video_file_id)

        if file is None: return "error security check if file access file failed"

        return update_sequence_shared(
            session, project, file.id, sequence_id, input['mode'], input['payload'])


@routes.route('/api/v1/task/<int:task_id>'
              '/sequence/<int:sequence_id>'
              '/update',
              methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def update_sequence_using_task_id(task_id, sequence_id):
    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = update_sequence_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        task = Task.get_by_id(
            session = session,
            task_id = task_id)

        if task is None: return "error security check if file access file failed"

        return update_sequence_shared(
            session, task.project, task.file_id, sequence_id, input['mode'], input['payload'])


def update_sequence_shared(
    session,
    project,
    file_id: int,
    sequence_id: int,
    mode: str,
    payload):
    """
    CAUTION if there are things that depend / stored
    on both sequence and instance will also need to updated here over time
    ie if we add something else that is unique to each sequence
    but stored on instance (like the "Number").

    Assumes sequence is valid if file id matches.
    Assumes label file is valid if it matches project.

    verifying label file
    alternatively look at implmentation in annotation.py
    ie get_allowed_label_file_ids()

    This is pretty "basic" right now... maybe other stuff
    to think about in terms of what to update...

    The number could conflict... Need to update number to highest
    could also just set it to big number...
    """

    if file_id is None or sequence_id is None or payload is None:
        return "a required argument is none", 400, {'ContentType': 'application/json'}

    log = regular_log.default()

    sequence = session.query(Sequence).filter(
        Sequence.video_file_id == file_id,
        Sequence.id == sequence_id).first()

    if sequence is None:
        return jsonify("Not found"), 400

    if mode == "update_label":

        if sequence.label_file_id == payload.get('id'):
            log['error']['label_file_id'] = "Same label selected, nothing to change."
            return jsonify(log = log), 400

        label_file = File.get_by_id_and_project(
            project_id = project.id,
            session = session,
            file_id = payload.get('id')
        )

        if label_file is None:
            return jsonify("Not found"), 400

        highest_sequence_in_new_context = Sequence.get_by_highest_number(
            session = session,
            video_file_id = file_id,
            label_file_id = label_file.id
        )

        if highest_sequence_in_new_context:
            new_sequence_number: int = highest_sequence_in_new_context.number + 1
        else:
            new_sequence_number: int = 1

        # dict, order may disaply different on front end.

        log['info']['moved_sequence_to_label_file'] = "Updated to: '" + \
                                                      label_file.label.name + "'. Click the label to see it."

        log['info']['new_sequence_number'] = "Updated sequence number to: " + \
                                             str(new_sequence_number)

        sequence.number = new_sequence_number
        sequence.label_file = label_file

        session.add(sequence)

    instances_updated_count = 0

    for instance in sequence.instance_list:

        if mode == "update_label":
            instance.label_file_id = label_file.id
            instance.number = new_sequence_number
            session.add(instance)
            instances_updated_count += 1

    # TODO would prefer to just get frames relevant to sequence...
    file_list = WorkingDirFileLink.image_file_list_from_video(
        session = session,
        video_parent_file_id = file_id
    )
    # Future, something like -> sequence.frame_list(session)
    for file in file_list:
        file.set_cache_key_dirty('instance_list')
        session.add(file)

    log['info']['instances_updated'] = "Updated " + str(instances_updated_count) + \
                                       " Instance(s)."

    log['success'] = True
    return jsonify(log = log), 200
