try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.annotation.instance_template import InstanceTemplate
from shared.annotation import Annotation_Update


@routes.route('/api/v1/project/<string:project_string_id>/instance-template/new', defaults={'task_id': None}, methods = ['POST'])
@routes.route('/api/v1/task/<int:task_id>/instance-template/new', methods=['POST'],  defaults={'project_string_id': None})
@PermissionTaskOrProject.by_task_or_project_wrapper(
    apis_user_list = ["builder_or_trainer"],
    roles = ["admin", "Editor", "Viewer"])
def new_instance_template_api(project_string_id, task_id):
    """
        Create a new instance template.
    :param project_string_id:
    :return:
    """
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
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = instance_template_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        if task_id:
            task = Task.get_by_id(session, task_id)
            project = task.project
        else:
            project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        new_instance_template_data, log = new_instance_template_core(
            session = session,
            log = log,
            member = member,
            name = input['name'],
            project = project,
            instance_list = input['instance_list'],
            reference_height = input['reference_height'],
            reference_width = input['reference_width'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(instance_template = new_instance_template_data), 200


def new_instance_template_core(session,
                               member,
                               name,
                               project,
                               instance_list,
                               reference_height,
                               reference_width,
                               log = regular_log.default()):
    """
        Creates a new instance template. It first creates the related instances and then saves the template
        and instances relations.
    :param session:
    :param log:
    :param member:
    :param project:
    :param instance_list:
    :param reference_height:
    :param reference_width:
    :return:
    """
    result = None
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

    if len(annotation_update.log['error'].keys()) >= 1:
        return None, annotation_update.log

    instance_template = InstanceTemplate.new(
        session = session,
        name = name,
        project = project,
        instance_list = new_instances,
        member_created = member,
        reference_height = reference_height,
        reference_width = reference_width

    )
    result = instance_template.serialize(session)
    return result, log
