from methods.regular.regular_api import *

from shared.database.attribute.attribute_template import Attribute_Template
from shared.database.attribute.attribute_template_group import Attribute_Template_Group


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/attribute/template/list',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor", "Viewer"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
def api_attribute_template_list(project_string_id):
    """

    """

    spec_list = [
        {'group_id': None},
        {'mode': None},
        {'with_labels': None}]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        project = Project.get(session, project_string_id)

        # TODO better handling if mode is invalid...
        if input['mode'] != "from_project":
            log['error']['mode'] = "Invalid mode"
            return jsonify(log = log), 400

        group_list = Attribute_Template_Group.list(
            session = session,
            group_id = input['group_id'],
            project_id = project.id,
            return_kind = "objects"
        )

        group_list_serialized = []

        for group in group_list:
            if input['with_labels'] is True:
                group_list_serialized.append(group.serialize_with_attributes_and_labels(session = session))

            else:
                group_list_serialized.append(group.serialize_with_attributes(session = session))

        log['success'] = True

        out = jsonify(
            attribute_group_list = group_list_serialized,
            log = log)
        return out, 200
