from methods.regular.regular_api import *

@routes.route('/api/v1/project/<string:project_string_id>/workflow/<int:workflow_id>/actions/<int:action_id>/manual_trigger',
              methods = ['PUT'])
@Project_permissions.user_has_project(
    Roles = ["admin", "Editor"],
    apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_action_manual(project_string_id, workflow_id, action_id):
    """

    """
    with sessionMaker.session_scope() as session:
        project = Project.get(session, project_string_id)
        member = get_member(session)

        Event.new(
            session = session,
            kind = "manual_trigger",
            action_id = action_id,
            member = member,
            project_id = project.id,
            workflow_id = workflow_id
        )

        return jsonify()