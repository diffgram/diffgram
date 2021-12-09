from methods.regular.regular_api import *

from shared.database.action.action import Action
from shared.database.action.action_flow import Action_Flow


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/action/reorder',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_reorder(project_string_id):
    """
    Shared route for update and new

    """

    spec_list = [
        {'flow_id': int},
        {'action_list': list},
        {'mode': str}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:

        user = User.get(session=session)
        project = Project.get(session, project_string_id)

        flow = Action_Flow.get_by_id(
            session=session,
            id=input['flow_id'],
            project_id=project.id)

        if flow is None:
            log['error']['flow'] = "No Flow found"
            return jsonify(log=log), 400

        # Caution, declaring as user.member for now.
        member = user.member

        ### WIP WIP WIP

        action_order = Action_Reorder(
            session=session,
            member=member,
            project=project,
            flow=flow,
            log=log,
            action_list=input['action_list'],
            mode=input['mode']
        )

        if len(action_session.log["error"].keys()) >= 1:
            return jsonify(log=log), 400

        # TODO return new list??? or just confirm ok??

        log['success'] = True

        out = jsonify(action=action.serialize(),
                      log=log)
        return out, 200


class Action_Reorder():
    """
    Holding class so we don't have to keep calling
    session and project for each function

    It's a bit of pain upfront but then class can grow as much as needed
    """

    def __init__(
            self,
            session,
            member,
            project,
            flow,
            log,
            action_list_untrusted,
            mode
    ):
        self.session = session
        self.member = member
        self.project = project
        self.mode = mode
        self.log = log
        self.flow = flow

        # This is the list from front end of action objects
        self.action_list_untrusted = action_list_untrusted

    ### WIP WIP WIP
    def reorder(self):
        pass

        # Get action list from shared.database

        # Set new relationships based on front end order

        # First action special case, then

        # start action list from second one
        self.action = something

        for action_untrusted in self.action_list_untrusted:
            # TODO get action from db
            action =  # something from action_untrusted

            self.action.child_primary = action

            # Swap action to be new one
            self.action = action
