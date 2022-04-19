# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment
from sqlalchemy.orm.session import Session
from shared.database.auth.member import Member
from shared.database.labels.label_schema import LabelSchema


@routes.route('/api/v1/project/<string:project_string_id>/labels-schema/<int:schema_id>/update', methods = ['PATCH'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_label_schema_update(project_string_id: str, schema_id: int):
    """
        List all the labels schemas of the given project.

    :param project_string_id:
    :return:
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
        request = request,
        spec_list = issue_new_spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        log = regular_log.default()
        label_schema_data, log = label_schema_update_core(
            session = session,
            project = project,
            member = member,
            schema_id = schema_id,
            name = input['name'],
            archived = input['archived'],
            log = log,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(label_schema_data), 200


def label_schema_update_core(session: Session,
                             project: Project,
                             name: str,
                             schema_id: int,
                             archived: bool,
                             member: Member,
                             log = regular_log.default()) -> [list, dict]:
    """
        Lists all the label schemas of the given project.
    :param session:
    :param project:
    :param name:
    :param archived:
    :param member:
    :param log:
    :return:
    """

    schema = LabelSchema.get_by_id(
        session = session,
        id = schema_id
    )
    if schema.project_id != project.id:
        log['error']['project_id'] = 'Schema Does not belong to given project.'
        return None, log

    schema.name = name
    schema.archived = archived
    schema.member_updated_id = member.id

    session.add(schema)

    result = schema.serialize()

    return result, log
