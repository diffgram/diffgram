# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion


@routes.route('/api/v1/project/<string:project_string_id>/issues/new', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def new_discussion_web(project_string_id):
    """
        Creates a new discussion with the given title, content and attached elements.
    :param project_string_id:
    :return:
    """
    issue_new_spec_list = [
        {"title": {
            'kind': str
        }},
        {"description": {
            'kind': str
        }},
        {"type": {
            'kind': str
        }},
        {"attached_elements": {
            'kind': list,
        }},
        {"marker_frame_number": {
            'kind': int,
        }},
        {"marker_type": {
            'kind': str,
        }},
        {"marker_data": {
            'kind': dict,
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
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        issue_data, log = new_discussion_core(
            session = session,
            log = log,
            member = member,
            project = project,
            title = input['title'],
            description = input['description'],
            marker_frame_number = input['marker_frame_number'],
            marker_type = input['marker_type'],
            marker_data = input['marker_data'],
            type = input['type'],
            attached_elements = input['attached_elements'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(issue = issue_data), 200


def new_discussion_core(session,
                        log = regular_log.default(),
                        member = None,
                        project = None,
                        title = None,
                        description = None,
                        marker_frame_number = None,
                        marker_type = None,
                        type = 'issue',
                        marker_data = None,
                        attached_elements = []):
    """
        Returns the created discussion as a python dictionary.
    :param session:
    :param log:
    :param member:
    :param project:
    :param title:
    :param description:
    :param attached_elements:
    :return: created discussion python dict.
    """
    if project is None:
        log['error']['project'] = 'Provide project for issue creation.'
        return None, log

    if title is None:
        log['error']['title'] = 'Provide title for issue creation.'
        return None, log

    if description is None:
        log['error']['description'] = 'Provide description for issue creation.'
        return None, log

    issue = Discussion.new(
        session = session,
        title = title,
        description = description,
        marker_frame_number = marker_frame_number,
        marker_type = marker_type,
        marker_data = marker_data,
        project_id = project.id,
        type = type,
        member_created_id = member.id if member else None
    )
    if attached_elements is not None:
        for element in attached_elements:
            issue.attach_element(session, element)

    issue_data = issue.serialize(session = session)
    return issue_data, log
