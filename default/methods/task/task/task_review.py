from methods.regular.regular_api import *
from shared.database.task.task import Task, TASK_STATUSES
from shared.database.task.task_event import TaskEvent
from shared.utils.task.task_update_manager import Task_Update
from shared.database.discussion.discussion_comment import DiscussionComment
from shared.utils.task import task_complete


@routes.route('/api/v1/task/<int:task_id>/review', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def task_review_api(task_id):
    """

    """
    spec_list = [{'comment': {
        'kind': str,
        'required': False
    }},
        {'action': {
            'kind': str,
            'valid_values_list': ['approve', 'request_change']
        }}
    ]

    log, input, untrusted_input = regular_input.master(request = request,
                                                       spec_list = spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:
        user = User.get(session)
        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        task_serialized = task_review_core(session = session,
                                           task_id = task_id,
                                           action = input['action'],
                                           member = member,
                                           comment_text = input['comment'])

        if task_serialized is False:
            log['info']['task'] = "No Task Found"
            return jsonify(log = log), 200

        log['success'] = True
        return jsonify(log = log,
                       task = task_serialized), 200


def task_review_core(session,
                     task_id: int,
                     action: str,
                     member: 'Member',
                     comment_text: str = None):
    task = Task.get_by_id(session, task_id = task_id)
    task_update_manager = Task_Update(
        session = session,
        task = task,
        member = member,
    )
    if action == 'approve':
        task_complete.task_complete(
            session = session,
            task = task,
            new_file = task.file,
            project = task.project,
            member = member,
            post_review = True)
    if action == 'request_change':
        task_update_manager.status = TASK_STATUSES['requires_changes']
        task_update_manager.main()

    if comment_text:
        discussion_comment = DiscussionComment.new(
            session = session,
            content = comment_text,
            member_created_id = member.id,
            project_id = task.project.id,
            user_id = member.user_id
        )
        TaskEvent.generate_task_comment_event(session = session,
                                              task = task,
                                              member = member,
                                              comment = discussion_comment)

    return task.serialize_builder_view_by_id(session)
