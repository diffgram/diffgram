# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment


@routes.route('/api/v1/project/<string:project_string_id>/discussion/<int:discussion_id>/update-comment',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def update_discussion_comment_web(project_string_id, discussion_id):
    """
        Update comment's content of the given comment_id in the POST payload.
    :param project_string_id:
    :param discussion_id:
    :return:
    """
    # For now, no filters needed. But might add in the future.
    issue_new_spec_list = [
        {"comment_id": {
            'kind': int
        }},
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
        discussion = Discussion.get_by_id(session, id = discussion_id)
        if discussion is None:
            log['error']['discussion'] = 'Discussion ID not found'
            return jsonify(log = log), 400

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        comment_data, log = update_discussion_comments_core(
            session = session,
            log = log,
            comment_id = input['comment_id'],
            member = member,
            content = input['content']
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(comment = comment_data), 200


def update_discussion_comments_core(session,
                                    comment_id,
                                    member,
                                    content,
                                    log = regular_log.default()):
    """
        Updates a comment. At this point we assume data has been validated so no extra checks are
        done to the input data. Only check is for permissions of edition. We do not allow editing
        comments of another user other than the one that has created the original comment.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """
    comment = DiscussionComment.get_by_id(session = session, id = comment_id)
    if member.id != comment.member_created_id:
        log['error']['member'] = 'Member cannot update the comment authored by another member. (Permission denied).'
        return None, log

    comment = DiscussionComment.update(
        session = session,
        content = content,
        member = member,
        comment_id = comment_id
    )

    comment_data = comment.serialize()
    return comment_data, log
