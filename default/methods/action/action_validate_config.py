from methods.regular.regular_api import *

import re
from sqlalchemy.orm.session import Session
from shared.database.action.action import Action
from shared.database.auth.member import Member
from shared.database.action.workflow import Workflow
from shared.database.action.action_template import Action_Template
from shared.data_tools_core import Data_tools

import tempfile
import os
from werkzeug.utils import secure_filename
from shared.image_tools import imresize
from imageio import imwrite


@routes.route('/api/v1/project/<string:project_string_id>/actions/<int:action_id>/validate',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_validate(project_string_id, action_id):
    """
        Validates the actions configurations are correct.

    """
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        user = User.get(session = session)
        member = get_member(session)
        project = Project.get(session, project_string_id)

        result, log = action_validate_core(
            session = session,
            project = project,
            member = member,
            action_id = action_id,
            log = log,
        )

        # For init errors
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        #
        out = jsonify(action = result,
                      log = log)
        return out, 200


def action_validate_core(session: Session,
                         project: Project,
                         member: Member,
                         action_id: int,
                         log: dict):

    return False, log
