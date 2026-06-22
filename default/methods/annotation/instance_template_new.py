# Import necessary modules and classes
from methods.regular.regular_api import *  # Import regular API methods
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation  # Import class for instance template relations
from shared.database.annotation.instance_template import InstanceTemplate  # Import class for instance templates
from shared.annotation import Annotation_Update  # Import class for annotation updates
from shared.database.labels.label_schema import LabelSchema  # Import class for label schemas

# Define the API endpoint for creating a new instance template
@routes.route('/api/v1/project/<string:project_string_id>/instance-template/new', defaults={'task_id': None}, methods = ['POST'])
@routes.route('/api/v1/task/<int:task_id>/instance-template/new', methods=['POST'],  defaults={'project_string_id': None})
@PermissionTaskOrProject.by_task_or_project_wrapper(
    apis_user_list = ["builder_or_trainer"],
    roles = ["admin", "Editor", "Viewer"])
def new_instance_template_api(project_string_id, task_id):
    """
        Create a new instance template.
    :param project_string_id: The string ID of the project associated with the new instance template
    :param task_id: The ID of the task associated with the new instance template (optional)
    :return: A JSON response containing the new instance template data
    """
    # Define the input specifications for creating a new instance template
    instance_template_new_spec_list = [
        {"name": {
            'kind': str
        }},
        {"instance_list": {
            'kind': list
        }},
        {"reference_width": {
            'kind': int
        }},
        {"reference_height": {
            'kind': int
        }},
        {"schema_id": {
            'kind': int,
            'required': True
        }},
    ]

    # Validate the input data and extract the relevant information
    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = instance_template_new_spec_list)

    # If the validation fails, return an error message to the client
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    # Create a new instance template using the input data
    with sessionMaker.session_scope() as session:
        if task_id:
            task = Task.get_by_id(session, task_id)
            project = task.project
        else:
            project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)

        # Determine the current user and their member object
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        # Create the new instance template and return the result to the client
        new_instance_template_data, log = new_instance_template_core(
            session = session,
            log = log,
            member = member,
            name = input['name'],
            project = project,
            instance_list = input['instance_list'],
            reference_height = input['reference_height'],
            reference_width = input['reference_width'],
            schema_id = input['schema_id'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(instance_template = new_instance_template_data), 200

# Define the function for creating a new instance template
def new_instance_template_core(session,
                               member,
                               name,
                               project,
                               instance_list,
                               reference_height,
                               reference_width,
                               schema_id,
                               log = regular_log.default()):
    """
        Creates a new instance template. It first creates the related instances and then saves the template
        and instances relations.
    :param session: The database session object
    :param log: The log object for recording errors and messages
    :param member: The member object for the current user
    :param project: The project object associated with the new instance template
    :param instance_list: The list of instances to be created
    :param reference_height: The reference height for the new instance template
    :param reference_width: The reference width for the new instance template
    :return: The new instance template data
    """
    # Get the label schema associated with the new instance template
    schema = LabelSchema.get_by_id(session, schema_id, project.id)
    if schema.project_id != project.id:
        log['error']['schema_id'] = 'Schema does not belong to project'
        return None, log

    # Create new instances based on the input data
    annotation_update = Annotation_Update(
        session = session,
        file = None,
        project = project,
        instance_list_new = instance_list,
        creating_for_instance_template = True,
        do_init_existing_instances = False
    )
    annotation_update.instance_template_main()
    new_instances = annotation_update.new_added_instances

    # If the instance creation fails, return an error message to the client
    if len(annotation_update.log['error'].keys()) >= 1:
        return None, annotation_update.log

    # Save the new instance template and its relations to the database
    instance_template = InstanceTemplate.new(
        session = session,
        name = name,
        project = project,
        instance_list = new_instances,
        member_created = member,
        reference_height = reference_height,
        reference_width = reference_width

    )
    schema.add_instance_template(session = session,
                                 member_created_id = member.id,
                                 instance_template_id = instance_template.id)

    # Return the new instance template data to the client
    result = instance_template.serialize(session)
    return result, log
