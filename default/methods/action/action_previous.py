from methods.regular.regular_api import *  # Importing necessary functions from the regular_api module
from shared.database.action.action import Action  # Importing Action class from the action module
from shared.regular.regular_log import log_has_error  # Importing log_has_error function from the regular_log module
from flasgger import swag_from  # Importing swag_from decorator from the flasgger module

@routes.route('/api/v1/project/<string:project_string_id>/action/previous/<string:action_id>', methods=['GET'])  # Defining the API route and HTTP method
@Project_permissions.user_has_project(                                                                   # Applying the user_has_project permission decorator
    Roles=["admin", "Editor"],                                                                           
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@swag_from('../../docs/actions/action_previous.yml')  # Adding Swagger documentation
def api_action_previous(project_string_id, action_id):  # Defining the route function

    with sessionMaker.session_scope() as session:  # Starting a session within a context manager
        log = regular_log.default()  # Creating a log object

        project = Project.get(session, project_string_id)  # Retrieving the project by its string ID
        action = Action.get_by_id(session = session, id = action_id, project_id = project.id)  # Retrieving the action by its ID

        previous_action = action.get_previous_action(session=session).serialize()  # Retrieving the previous action and converting it to a dictionary

        if log_has_error(log) >= 1:  # Checking if there are any errors in the log
            return jsonify(log = log), 400  # Returning the log and a 400 Bad Request status code if errors are present

        out = jsonify(previous_action=previous_action, log=log)  # Preparing the response data
        return out, 200  # Returning the response data and a 200 OK status code
