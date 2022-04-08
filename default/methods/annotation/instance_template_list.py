try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.annotation.instance_template_relation import InstanceTemplateRelation
from shared.database.annotation.instance_template import InstanceTemplate
from shared.annotation import Annotation_Update
from shared.database.labels.label_schema import LabelSchema, LabelSchemaLink

@routes.route('/api/v1/project/<string:project_string_id>/instance-template/list', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "allow_if_project_is_public"],
                                      apis_user_list = ["api_enabled_builder"])
def list_instance_template_api(project_string_id):
    """
        Fetch the list of instance templates in the project.
    :param project_string_id:
    :return:
    """
    instance_template_list_spec_list = [{'schema_id': {'required': True, 'type': int}}]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = instance_template_list_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        new_instance_template_data, log = list_instance_templates_core(
            session = session,
            log = log,
            project = project,
            schema_id = input['schema_id'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(instance_template_list = new_instance_template_data), 200


def list_instance_templates_core(session,
                                 project,
                                 schema_id,
                                 log = regular_log.default()):
    """
       Returns a list of serialized instances templates matching the given project.
    :param session:
    :param log:
    :param member:
    :param project:
    :param instance_list:
    :return:
    """
    result = None
    schema = LabelSchema.get_by_id(session, schema_id)
    if schema.project_id != project.id:
        log['error']['schema_id'] = 'Schema does not belong to project'
        return None, log
    instance_template_list = InstanceTemplate.list(
        session = session,
        project = project,
        schema = schema
    )
    result = [template.serialize(session) for template in instance_template_list]
    return result, log
