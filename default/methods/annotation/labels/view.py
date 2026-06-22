@routes.route('/api/v1/project/<string:project_string_id>' + \
              '/labels/view/name_to_file_id',
              methods = ['GET'])
@Project_permissions.user_has_project(
    ["admin", "Editor", "Viewer", "allow_if_project_is_public"])
def web_build_name_to_file_id_dict(project_string_id):
    """
    View function to build a dictionary mapping label names to their corresponding IDs in the project's default schema or a specified schema.

    Args:
        project_string_id (str): The unique identifier of the project.

    Returns:
        A JSON response containing the name-to-file_id dictionary and log information.

    """
    log = regular_log.default()
    schema_id = request.args.get('schema_id')

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        name_to_file_id, log = build_name_to_file_id_dict(
            session = session,
            project = project,
            schema_id = schema_id,
            log = log)

        if regular_log.log_has_error(log):
            return jsonify(log), 400
        else:
            log["success"] = True

    return jsonify(log = log,
                   name_to_file_id = name_to_file_id), 200


def build_name_to_file_id_dict(
        session, 
        project, 
        log, 
        schema_id = None):
    """
    A helper function to build the name-to-file_id dictionary.

    Args:
        session: The database session.
        project: The Project object.
        log: The log object.
        schema_id (int, optional): The ID of the schema to use. Defaults to None.

    Returns:
        A tuple containing the name-to-file_id dictionary and the log object.

    """

    if schema_id is None:
        schema = project.get_default_schema(session = session)
        schema_id = schema.id
    else:
        schema = LabelSchema.get_by_id(session = session, id = schema_id, project_id = project.id)
        if not schema:
            log['error']['schema'] = 'Label Schema not found'
            return None, log
        if schema.project_id != project.id:
            log['error']['schema'] = 'Schema does not belong to project.'
            return None, log

    label_file_list = project.get_label_list(
        session = session,
        directory = project.directory_default,
        schema_id = schema_id)

    out = {}

    for elm in label_file_list:
        out[elm['label']['name']] = elm['id']

    return out, log
