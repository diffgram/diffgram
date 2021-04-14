# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment


@routes.route('/api/v1/project/<string:project_string_id>/discussion/<int:discussion_id>/add-comment',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def new_discussion_comment_web(project_string_id, discussion_id):
    """
        Create a new comment on the given discussion_id.
        The comment content will be an HTML string.
    :param project_string_id:
    :param discussion_id:
    :return:
    """
    issue_new_spec_list = [
        {"content": {
            'kind': str
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)
        discussion = Discussion.get_by_id(session, id=discussion_id)
        if discussion is None:
            log['error']['discussion'] = 'Discussion ID not found'
            return jsonify(log = log), 400

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        comment_data, log = new_discussion_comment_core(
            session = session,
            log = log,
            member = member,
            user = user,
            project = project,
            discussion = discussion,
            content = input['content']
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(comment = comment_data), 200


def new_discussion_comment_core(session,
                                member,
                                user,
                                project,
                                discussion,
                                content,
                                log = regular_log.default()):
    """
        Creates a new comment. At this point we assume data has been validated so no extra checks are
        done to the input data.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """
    comment = DiscussionComment.new(
        session = session,
        content = content,
        member_created_id = member.id,
        project_id = project.id,
        user_id = user.id if user else None,
        member_updated_id = member.id,
        discussion_id = discussion.id
    )

    comment_data = comment.serialize()
    return comment_data, log
