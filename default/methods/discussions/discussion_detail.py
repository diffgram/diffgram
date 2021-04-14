# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion


@routes.route('/api/v1/project/<string:project_string_id>/issues/<int:discussion_id>', methods = ['GET'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def discussion_detail_web(project_string_id, discussion_id):
    """
        Get discussion detail. This will include all attached elements.
    :param project_string_id:
    :param discussion_id:
    :return:
    """
    with sessionMaker.session_scope() as session:
        log = regular_log.default()
        project = Project.get_by_string_id(session, project_string_id)

        issue_data, log = discussion_detail_core(
            session = session,
            log = log,
            project = project,
            discussion_id = discussion_id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(issue = issue_data), 200


def discussion_detail_core(session,
                           log = regular_log.default(),
                           project = None,
                           discussion_id = None):
    """
        Return serialized dictionary with data of the given discussion.
    :param session:
    :param log:
    :param project:
    :param discussion_id:
    :return: dictionary of the given discussion data.
    """

    discussion = Discussion.get_by_id(session, id = discussion_id)

    if discussion.project_id != project.id:
        log['error']['project_id'] = 'Wrong project ID provided.'

    if discussion is None:
        log['error']['discussion_id'] = 'discussion ID not found'
        return None, log

    issue_data = discussion.serialize(session = session)
    return issue_data, log
