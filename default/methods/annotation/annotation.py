# This script is part of the OpenCore project and contains functions for adding annotations
# to a file via the project API or a task API.

from methods.regular.regular_api import *  # Importing functions from the regular API module

# Importing annotation update functions for the project and task APIs
from shared.annotation import annotation_update_web, task_annotation_update

# Importing the route for annotation update for the project API
@routes.route('/api/project/<string:project_string_id>/file/<int:file_id>/annotation/update', methods=['POST'])
# Checking if the user has the required permissions for the project
@Project_permissions.user_has_project(["admin", "Editor"])
# Function for updating annotations via the project API
def annotation_update_via_project_api(project_string_id, file_id):
    log = regular_log.default()  # Creating a default log object
    with sessionMaker.session_scope() as session:
        # Calling the annotation update web function to update annotations
        new_file, annotation_update = annotation_update_web(
            session=session,
            project_string_id=project_string_id,
            file_id=file_id,
            log=log)

        # Checking if there are any errors in the log object
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Checking if there are any errors in the annotation update log object
        if len(annotation_update.log["error"].keys()) >= 1:
            return jsonify(log=annotation_update.log), 400

        # Extracting the required information from the annotation update object
        sequence = None
        new_sequence_list = []
        if annotation_update.sequence:
            sequence = annotation_update.sequence.serialize_for_label_subset(
                session=session)
        if annotation_update.new_created_sequence_list:
            new_sequence_list = [seq.serialize_for_label_subset(session=session) for seq in annotation_update.new_created_sequence_list]
        deleted_instances = annotation_update.new_deleted_instances
        added_instances = annotation_update.new_added_instances
        # Serializing all the instances for the frontend to render them correctly
        added_instances = [x.serialize() for x in added_instances]

        # Returning the updated annotations and other relevant information
        return jsonify(
            success=True,
            log=annotation_update.log,
            new_file=new_file,
            added_instances=added_instances,
            deleted_instances=deleted_instances,
            new_sequence_list=new_sequence_list,
            sequence=sequence), 200

# Importing the route for annotation update for the task API
@routes.route('/api/v1/task/<int:task_id>/annotation/update', methods=['POST'])
# Checking if the user has the required permissions for the task
@Permission_Task.by_task_id(apis_user_list=["builder_or_trainer"])
# Function for updating annotations via the task API
def task_annotation_update_api(task_id):
    # Specifying the required input format for the function
    spec_list = [{"instance_list": None},
                 {"and_complete": bool},
                 {"child_file_save_id": {
                     "required": False,
                     "kind": int
                 }},
                 {"video_data": {
                     'kind': dict,
                     'default': None
                 }
                 }]

    # Validating the input format and creating log and input objects
    log, input, untrusted_input = regular_input.master(request=request, spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # MAIN
    with sessionMaker.session_scope() as session:
        # Getting the member object for the current session
        member = get_member(session=session)
        # Calling the task annotation update function to update annotations
        new_file, annotation_update = task_annotation_update(
            session=session,
            task_id=task_id,
            input=input,
            member=member,
            untrusted_input=untrusted_input,
            log=log)

        # Checking if there are any errors in the log object
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Checking if there are any errors in the annotation update log object
        if len(annotation_update.log["error"].keys()) >= 1:
            return jsonify(log=annotation_update.log), 400

        # Extracting the required information from the annotation update object
        sequence = None
        if annotation_update.sequence:
            sequence = annotation_update.sequence.serialize_for_label_subset(session=session)

        new_sequence_list = []
        if annotation_update.new_created_sequence_list:
            new_sequence_list = [seq.serialize_for_label_subset(session=session) for seq in annotation_update.new_created_sequence_list]

        deleted_instances = annotation_update.new_deleted_instances
        added_instances = annotation_update.new_added_instances
        # Serializing all the instances for the frontend to render them correctly
        added_instances = [x.serialize() for x in added_instances]

        # Returning the updated annotations and other relevant information
        return jsonify(
            success=True,
            log=annotation_update.log,
            new_file=new_file,
            added_instances=added_instances,
            deleted_instances=deleted_instances,
            new_sequence_list=new_sequence_list,
            sequence=sequence), 200
