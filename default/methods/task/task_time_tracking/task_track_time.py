# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment


@routes.route('/api/v1/task/<int:task_id>', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def api_task_track_time(task_id):
    """
        Track time spent on task by a specific user

    :param task_id:
    :return:
    """
    # For now, no filters needed. But might add in the future.
    issue_new_spec_list = []

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = issue_new_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, task_id)
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

        comments_data, log = list_discussion_comments_core(
            session = session,
            log = log,
            project = project,
            discussion = discussion,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(comments = comments_data), 200


def list_discussion_comments_core(session,
                                  project,
                                  discussion,
                                  log = regular_log.default()):
    """
        List comments of the discussion. At this point we assume data has been validated so no extra checks are
        done to the input data.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """
    comments = DiscussionComment.list(
        session = session,
        project_id = project.id,
        discussion_id = discussion.id
    )

    comment_data = [comment.serialize() for comment in comments]
    return comment_data, log
