from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.workflow import Workflow
from shared.database.action.workflow_run import WorkflowRun
from flasgger import swag_from

# NEW
@routes.route('/api/v1/project/<string:project_string_id>' +
              '/actions/workflow/new',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=["api_enabled_builder"])
@limiter.limit("1000 per day")
@swag_from('../../docs/actions/workflow_new.yml')
def new_workflow_factory_api(project_string_id):
    """
    Create a new workflow object with the given name and associate it with the
    specified project. This function returns the newly created workflow's id.

    Parameters:
    project_string_id (str): The unique identifier of the project.

    Returns:
