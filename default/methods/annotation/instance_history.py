try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


@routes.route('/api/v1/project/<string:project_string_id>/instance/<int:instance_id>/history', methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor", "Viewer"], apis_user_list = ["api_enabled_builder"])
def instance_history_api(project_string_id, instance_id):
    """
        This function creates a new instance template by calling the instance_history_core function.
        
        It first imports the required functions and modules. Then, it validates the user permissions
        to access the project using the Project_permissions.user_has_project decorator. 

        :param project_string_id: The unique string ID of the project.
        :param instance_id: The unique ID of the instance.
        :return: A JSON response containing the instance history data or an error message.
    """
    instance_history_spec_list = []

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = instance_history_spec_list)

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

        instance_history_data, log = instance_history_core(
            session = session,
            instance_id = instance_id,
            project = project,
            log = log,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(instance_history = instance_history_data), 200


def instance_history_core(
        session, 
        instance_id: int, 
        project, 
        log = regular_log.default()):
    """
        This function creates a new instance template by first creating the related instances and then saving
        the template and instances relations.

        :param session: SQL Alchemy Session.
        :param log: regular_log
        :param root_id: int
        :return: A tuple containing the instance history data and the log.
    """
    if project is None:
        log['error']['project'] = 'Provide project object.'
        return False, log

    if instance_id is None:
        log['error']['root_id'] = 'Provide instance_id'
        return False, log

    instance_child = Instance.get_by_id(session = session, instance_id = instance_id)
    if instance_child.project_id != project.id:
        log['error']['project_missmatch'] = 'Instance does not belong to the project.'
        return False, log

    if instance_child.root_id is None:  # We can still return itself
        log['info']['root_id'] = 'Instance has no root ID'
        return [instance_child.serialize_with_member_data(session)], log

    history_list = Instance.get_child_instance_history(
        session = session, 
        root_id = instance_child.root_id)
    
    history_serialized = [instance.serialize_with_member_data(session) for instance in history_list]

    return history_serialized, log
