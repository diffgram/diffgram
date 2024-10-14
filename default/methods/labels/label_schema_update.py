# OPENCORE - ADD
import json
from typing import List, Dict

from methods.regular.regular_input import regular_input
from methods.regular.regular_log import regular_log
from methods.shared.database.discussion import Discussion, DiscussionComment
from methods.shared.database.session import sessionMaker
from methods.shared.database.auth.member import Member
from methods.shared.database.labels.label_schema import LabelSchema, Project

# Routing for the API endpoint to update a label schema
@routes.route('/api/v1/project/<string:project_string_id>/labels-schema/<int:schema_id>/update', methods=['PATCH'])
@Project_permissions.user_has_project(Roles=["admin", "Editor"], apis_user_list=["api_enabled_builder"])
def api_label_schema_update(project_string_id: str, schema_id: int):
    """
        Update a label schema in the given project.

    :param project_string_id: The string ID of the project.
    :param schema_id: The ID of the label schema to update.
    :return: A JSON response containing the updated label schema or an error message.
    """
    issue_new_spec_list = [
        {"name": {
            'kind': str,
            'required': True
        }},
        {"archived": {
            'kind': bool,
            'required': True
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=issue_new_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        log = regular_log.default()
        label_schema_data, log = label_schema_update_core(
            session=session,
            project=project,
            member=member,
            schema_id=schema_id,
            name=input['name'],
            archived=input['archived'],
            log=log,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        return jsonify(label_schema_data), 200


def label_schema_update_core(session: Session,
                             project: Project,
                             name: str,
                             schema_id: int,
                             archived: bool,
                             member: Member,
                             log: Dict = regular_log.default()) -> (List, Dict):
    """
        Update a label schema in the given project.

    :param session: The database session.
    :param project: The project containing the label schema.
    :param name: The new name of the label schema.
    :param schema_id: The ID of the label schema to update.
    :param archived: Whether the label schema should be archived.
    :param member: The member updating the label schema.
    :param log: The log dictionary to store messages.
    :return: The updated label schema or an error message.
    """

    schema = LabelSchema.get_by_id(
        session=session,
        id=schema_id,
        project_id=project.id)
    if schema is None:
        log['error']['project_id'] = 'Schema Does not belong to given project.'
        return None, log

    schema.name = name
    schema.archived = archived
    schema.member_updated_id = member.id

    session.add(schema)

    result = schema.serialize()

    return result, log
