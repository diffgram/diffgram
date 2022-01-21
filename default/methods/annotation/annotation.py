# OPENCORE - ADD
from methods.regular.regular_api import *

# See Shared/annotation for majority of current methods here due to monolith change
from shared.annotation import annotation_update_web
from shared.annotation import task_annotation_update


@routes.route('/api/project/<string:project_string_id>/file/<int:file_id>/annotation/update',
              methods = ['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def annotation_update_via_project_api(project_string_id, file_id):
    log = regular_log.default()
    with sessionMaker.session_scope() as session:

        new_file, annotation_update = annotation_update_web(
            session = session,
            project_string_id = project_string_id,
            file_id = file_id,
            log = log)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        if len(annotation_update.log["error"].keys()) >= 1:
            return jsonify(log = annotation_update.log), 400

        sequence = None
        new_sequence_list = []
        if annotation_update.sequence:
            sequence = annotation_update.sequence.serialize_for_label_subset(
                session = session)
        if annotation_update.new_created_sequence_list:
            new_sequence_list = [seq.serialize_for_label_subset(session = session) for seq in annotation_update.new_created_sequence_list]
        deleted_instances = annotation_update.new_deleted_instances
        added_instances = annotation_update.new_added_instances
        # We need to serialize all the instances for the frontend to render them correctly.
        added_instances = [x.serialize() for x in added_instances]

        return jsonify(
            success = True,
            log = annotation_update.log,
            new_file = new_file,
            added_instances = added_instances,
            deleted_instances = deleted_instances,
            new_sequence_list = new_sequence_list,
            sequence = sequence), 200


@routes.route('/api/v1/task/<int:task_id>/annotation/update', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_annotation_update_api(task_id):
    # None for now since may be empty if no changes
    """
    If the type is a video, we assume the front end will pass the correct frame_number
    to be used. We get the image file using the frame id and the task.file_id as the
    parent.

    """

    spec_list = [{"instance_list": None},
                 {"and_complete": bool},
                 {"video_data": {
                     'kind': dict,
                     'default': None
                 }
                 }]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    # MAIN
    with sessionMaker.session_scope() as session:
        member = get_member(session = session)
        new_file, annotation_update = task_annotation_update(
            session = session,
            task_id = task_id,
            input = input,
            member = member,
            untrusted_input = untrusted_input,
            log = log)

        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        if len(annotation_update.log["error"].keys()) >= 1:
            return jsonify(log = annotation_update.log), 400

        sequence = None
        if annotation_update.sequence:
            sequence = annotation_update.sequence.serialize_for_label_subset(
                session = session)

        new_sequence_list = []
        if annotation_update.new_created_sequence_list:
            new_sequence_list = [seq.serialize_for_label_subset(session = session) for seq in annotation_update.new_created_sequence_list]

        deleted_instances = annotation_update.new_deleted_instances
        added_instances = annotation_update.new_added_instances
        # We need to serialize all the instances for the frontend to render them correctly.
        added_instances = [x.serialize() for x in added_instances]

        return jsonify(
            success = True,
            log = annotation_update.log,
            new_file = new_file,
            added_instances = added_instances,
            deleted_instances = deleted_instances,
            new_sequence_list = new_sequence_list,
            sequence = sequence), 200
