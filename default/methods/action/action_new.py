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
from flasgger import swag_from

@routes.route('/api/v1/project/<string:project_string_id>/actions/workflow/<int:workflow_id>/action',
              methods = ['POST'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
@swag_from('../../docs/actions/actions_new.yml')
def api_action_new(project_string_id, workflow_id):
    """
    Shared route for update and new

    """

    spec_list = [
        {'public_name': str},
        {'kind': str},
        {'icon': str},
        {'description': str},
        {'template_id': int},
        {'workflow_id': int},
        {'ordinal': int},
        {'precondition':
            {
            'default': None,
            'kind': dict
            }
        },
        {'trigger_data': 
            {
            'default': None,
            'kind': dict
            }
        },
        {'completion_condition_data': 
            {
            'default': None,
            'kind': dict
            }
        }

    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session = session)
        member = get_member(session)
        project = Project.get(session, project_string_id)

        result, log = action_creation_core(
            session = session,
            project = project,
            member = member,
            public_name = input['public_name'],
            kind = input['kind'],
            description = input['description'],
            trigger_data = input['trigger_data'],
            precondition = input['precondition'],
            template_id = input['template_id'],
            completion_condition_data = input['completion_condition_data'],
            workflow_id = input['workflow_id'],
            ordinal = input['ordinal'],
            icon = input['icon'],
            log = log,
        )

        # For init errors
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400
        #
        # if action_session.mode in ["UPDATE", "ARCHIVE"]:
        #
        #     action_session.update_mode_init()
        #
        #     if len(action_session.log["error"].keys()) >= 1:
        #         return jsonify(log=log), 400
        #
        # action_session.route_kind_using_strategy_pattern()
        #
        # log = action_session.log
        # if len(log["error"].keys()) >= 1:
        #     return jsonify(log=log), 400
        #
        # action = action_session.action
        # log['success'] = True
        #
        # if action_session.mode == "NEW":
        #     # Just putting it here for now while
        #     # Figuring out how we are loading member
        #     # Probably could be in action_session()
        #     Event.new(
        #         session=session,
        #         kind="new_action",
        #         member=member,
        #         success=True,
        #         project_id=project.id,
        #         email=user.email
        #     )

        out = jsonify(action = result,
                      log = log)
        return out, 200


def action_creation_core(session: Session,
                         project: Project,
                         member: Member,
                         public_name: str,
                         icon: str,
                         kind: str,
                         description: str,
                         trigger_data: dict,
                         precondition: dict,
                         template_id: int,
                         workflow_id: int,
                         ordinal: int,
                         completion_condition_data: dict,
                         log: dict):
    workflow = Workflow.get_by_id(session = session, id = workflow_id, project_id = project.id)
    if workflow is None:
        log['error']['workflow'] = f'Workflow id {workflow_id} not found'
        return False, log

    action_template = Action_Template.get_by_id(session = session, id = template_id)
    if action_template is None:
        log['error']['action_template'] = f'Action template id {template_id} not found'
        return False, log

    if trigger_data.get('event_name') == None:
        trigger_data['event_name'] = trigger_data['default_event_name']

    action = Action.new(
        session = session,
        project = project,
        kind = kind,
        member = member,
        workflow = workflow,
        template = action_template,
        public_name = public_name,
        icon = icon,
        completion_condition_data = completion_condition_data,
        description = description,
        ordinal = ordinal,
        trigger_data = trigger_data,
        precondition = precondition,
    )

    res = action.serialize()

    return res, log


