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

@routes.route('/api/v1/project/<string:project_string_id>/labels-schema', methods = ['GET'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def api_label_schema_list(project_string_id: str):
    """
        List all the labels schemas of the given project.

    :param project_string_id:
    :return:
    """
    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id)
        member = get_member(session)
        log = regular_log.default()
        label_schema_data, log = label_schema_list_core(
            session = session,
            project = project,
            member = member,
            log = log,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(label_schema_data), 200


def label_schema_list_core(session: Session,
                           project: Project,
                           member: Member,
                           log = regular_log.default()) -> [list, dict]:
    """
        Lists all the label schemas of the given project.
    :param session:
    :param project:
    :param member:
    :param log:
    :return:
    """
    result = []

    schema_list = LabelSchema.list(
        session = session,
        project_id = project.id
    )

    result = [s.serialize() for s in schema_list]

    return result, log
