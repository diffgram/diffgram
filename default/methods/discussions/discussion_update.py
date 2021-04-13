# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion


@routes.route('/api/v1/project/<string:project_string_id>/discussion/<int:discussion_id>/update',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def update_discussion_web(project_string_id, discussion_id):
    """
        Update a discussion description, status or attached elements.
    :param project_string_id:
    :param discussion_id:
    :return:
    """

    # For now, no filters needed. But might add in the future.
    issue_new_spec_list = [
        {"description": {
            'kind': str,
            'required': False
        }},
        {"status": {
            'kind': str,
            'required': False
        }},
        {"attached_elements": {
            'kind': list,
            'allow_empty': True
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

        discussion_data, log = update_discussion_core(
            session = session,
            log = log,
            discussion = discussion,
            member = member,
            description = input['description'],
            status = input['status'],
            attached_elements = input['attached_elements']
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(discussion = discussion_data), 200


def update_discussion_core(session,
                           discussion,
                           member,
                           status = None,
                           description = None,
                           attached_elements = None,
                           log = regular_log.default()):
    """
       Updates a discussion. At this point we assume data has been validated so no extra checks are
        done to the input data.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """

    if member.id != discussion.member_created_id:
        log['error']['member'] = 'Member cannot update the discussion authored by another member. (Permission denied).'
        return None, log

    discussion = Discussion.update(
        session = session,
        description = description,
        status = status,
        attached_elements = attached_elements,
        discussion_id = discussion.id
    )

    discussion_data = discussion.serialize(session)
    return discussion_data, log
