# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.discussion.discussion import Discussion
from shared.database.discussion.discussion_comment import DiscussionComment


@routes.route('/api/v1/task/<int:task_id>', methods = ['POST'])
@Permission_Task.by_task_id(apis_user_list = ["builder_or_trainer"])
def api_task_track_time(task_id):
    """
        Track time spent on task by a specific user

    :param task_id:
    :return:
    """
    track_time_spec_list = [
        {"time_spent": {
            'kind': float,
            "required": True
        }},
        {"task_status": {
            'kind': str,
            "required": True
        }},
        {"file_id": {
            'kind': str,
            "required": True
        }},
        {"parent_file_id": {
            'kind': str,
            "required": True
        }},
        {"file_type": {
            'kind': str,
            "required": True
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = track_time_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, task_id)
        user = User.get(session)

        comments_data, log = track_time_core(
            session = session,
            project = project,
            task_id = task_id,
            task_status = input['task_status'],
            file_id = input['file_id'],
            parent_file_id = input['parent_file_id'],
            file_type = input['file_type'],
            user = user,
            log = log,

        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(comments = comments_data), 200


def track_time_core(session,
                    project,
                    task_id,
                    task_status,
                    file_id,
                    parent_file_id,
                    file_type,
                    user,
                    log = regular_log.default()):
    """
            Record a new Task Time Track record. This will save the record for the specific file
            and any aggregated records.
            If record already exists it will update to the new time_spent if the time is less than the
            current saved time.
    :param session:
    :param project:
    :param task_id:
    :param task_status:
    :param file_id:
    :param parent_file:
    :param file_type:
    :param user:
    :param log:
    :return:
    """


    return None, log
