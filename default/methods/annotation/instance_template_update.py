try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.annotation.instance_template import InstanceTemplate
from shared.annotation import Annotation_Update


@routes.route('/api/v1/project/<string:project_string_id>/instance-template/<int:instance_template_id>',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def update_instance_template_api(project_string_id, instance_template_id):
    """
        Create a new instance template.
    :param project_string_id:
    :return:
    """
    instance_template_new_spec_list = [
        {"name": {
            'kind': str,
            'required': False
        }},
        {"instance_list": {
            'kind': list,
            'required': False
        }},
        {"status": {
            'kind': str,
            'required': False
        }},
        {"mode": {
            'kind': str,
            'required': False
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = instance_template_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        new_instance_template_data, log = update_instance_template_core(
            session = session,
            log = log,
            member = member,
            name = input['name'],
            project = project,
            instance_list = input['instance_list'],
            status = input['status'],
            mode = input['mode'],
            instance_template_id = instance_template_id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(instance_template = new_instance_template_data), 200


def update_instance_template_core(session,
                                  member,
                                  project,
                                  instance_template_id,
                                  name = None,
                                  mode = None,
                                  instance_list = None,
                                  status = None,
                                  log = regular_log.default()):
    """
        Creates a new instance template. It first creates the related instances and then saves the template
        and instances relations.
    :param session:
    :param log:
    :param member:
    :param project:
    :param name:
    :param instance_list:
    :param status:
    :param instance_template_id:
    :return:
    """
    result = None
    if instance_list is not None:
        annotation_update = Annotation_Update(
            session = session,
            file = None,
            project = project,
            instance_list_new = instance_list,
            creating_for_instance_template = True,
            do_init_existing_instances = False
        )
        annotation_update.instance_template_main()

        if len(annotation_update.log['error'].keys()) >= 1:
            return None, annotation_update.log

    instance_template = InstanceTemplate.get_by_id(
        session = session,
        id = instance_template_id

    )
    if name is not None:
        instance_template.name = name
    if mode is not None:
        instance_template.mode = mode
    if status is not None:
        instance_template.status = status
    session.add(instance_template)
    result = instance_template.serialize(session)
    return result, log
