# OPENCORE - ADD
from methods.regular.regular_api import *
from shared.database.sync_events.sync_event import SyncEvent


@routes.route('/api/v1/<string:project_string_id>/user-visit-history/', methods=['POST'])
@Project_permissions.user_has_project(
    Roles=["admin", "Editor"],
    apis_user_list=['api_enabled_builder', 'security_email_verified'])
def user_visit_history_api(project_string_id):
    spec_list = [
        {
            'limit': int
        }
    ]
    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        member = get_member(session=session)
        project = Project.get_by_string_id(session, project_string_id = project_string_id)
        user_visit_events = user_visit_history_core(session=session,
                                                    project=project,
                                                    member=member,
                                                    limit=input.get('limit'))
        log['success'] = True
        return jsonify(log=log,
                       user_visit_events=user_visit_events), 200


def user_visit_history_core(session, project, member, limit=20):
    # Check Permissions
    event_list = session.query(Event).filter(
        Event.kind == 'user_visit',
        Event.member_id == member.id,
        Event.project_id == project.id
    ).order_by(Event.time_created.desc()).limit(limit).all()

    serialized_events = []
    if event_list:
        for event in event_list:
            serialized_events.append(event.serialize_for_visit_history(session))

    return serialized_events
