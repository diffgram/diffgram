# OPENCORE - ADD
# This block imports necessary modules and classes, including the 'Discussion' class from 'shared.database.discussion.discussion'.

@routes.route('/api/v1/project/<string:project_string_id>/discussion/<int:discussion_id>/update', methods=['POST'])
@Project_permissions.user_has_project(Roles=["admin", "Editor", "annotator"], apis_user_list=["api_enabled_builder"])
def update_discussion_web(project_string_id, discussion_id):
    """
    Update a discussion description, status, or attached elements.

    :param project_string_id: The string ID of the project.
    :param discussion_id: The ID of the discussion to be updated.
    :return: A JSON response containing the updated discussion data or an error message.
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

    # The 'regular_input.master' function validates the input data based on the 'issue_new_spec_list' specification.
    log, input, untrusted_input = regular_input.master(request=request, spec_list=issue_new_spec_list)

    # If there are any errors in the input data, return a 400 Bad Request response with the error log.
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    # The 'sessionMaker.session_scope()' creates a new database session.
    with sessionMaker.session_scope() as session:

        # Retrieve the project, user, and discussion using their respective IDs.
        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)
        discussion = Discussion.get_by_id(session, id=discussion_id)

        # If the discussion is not found, return a 400 Bad Request response with an error message.
        if discussion is None:
            log['error']['discussion'] = 'Discussion ID not found'
            return jsonify(log=log), 400

        # If the user is authenticated, retrieve their member information.
        # Otherwise, retrieve the member information using the client ID from the request's authorization header.
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        # Call the 'update_discussion_core' function to update the discussion.
        discussion_data, log = update_discussion_core(session=session, log=log, discussion=discussion, member=member, description=input['description'], status=input['status'], attached_elements=input['attached_elements'])

        # If there are any errors in the update process, return a 400 Bad Request response with the error log.
        if len(log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # Return a 200 OK response with the updated discussion data.
        return jsonify(discussion=discussion_data), 200


def update_discussion_core(session, log, member, status=None, description=None, attached_elements=None, discussion=None):
    """
    Updates a discussion. At this point, it is assumed that the data has been validated, so no extra checks are done to the input data.

    :param session: The database session.
    :param log: The log dictionary.
    :param member: The member updating the discussion.
    :param project: The project the discussion belongs to.
    :param discussion: The discussion to be updated.
    :param content: The new content of the discussion.
    :return: The updated discussion data and the log dictionary.
    """

    # Check if the member updating the discussion is the same as the member who created it.
    # If not, return an error message in the log dictionary.
    if member.id != discussion.member_created_id:
        log['error']['member'] = 'Member cannot update the discussion authored by another member. (Permission denied).'
        return None, log

    # Update the discussion with the new description, status, and attached elements.
    discussion = Discussion.update(session=session, description=description, status=status,
                                  attached_elements=attached_elements, discussion_id=discussion.id)

    # Serialize the updated discussion and return it along with the log dictionary.
    discussion_data = discussion.serialize(session)
    return discussion_data, log
