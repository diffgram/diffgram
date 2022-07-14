from methods.regular.regular_api import *

from sqlalchemy.orm.session import Session
from shared.database.action.action import Action
from shared.database.auth.member import Member
from shared.database.action.workflow import Workflow
from shared.database.action.action_template import Action_Template
from shared.data_tools_core import Data_tools


@routes.route('/api/v1/project/<string:project_string_id>/actions/<int:action_id>/manual_trigger',
              methods = ['PUT'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_manual(project_string_id, action_id):
    """

    """
    project = Project.get(session)
    action = Action.get_by_id(session, action_id, project.id)
    member = get_member(session)

    Event.new(
        session = session,
        kind = "manual_trigger",
        action_id = action.id,
        member_id = member.id,
        project_id = project.id
    )