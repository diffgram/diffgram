# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.batch.batch import InputBatch


@routes.route('/api/v1/project/<string:project_string_id>/input-batch/new',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def new_input_batch(project_string_id):
    """
        Create a new input Batch to attach inputs to it later.
    :param project_string_id:
    :param discussion_id:
    :return:
    """
    input_batch_spec_list = [
        {"pre_labeled_data": {
            'kind': dict,
            'required': False
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = input_batch_spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        batch_data, log = new_input_batch(
            session = session,
            log = log,
            member = member,
            project = project,
            user = user,
            pre_labeled_data = input['pre_labeled_data'],
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(input_batch = batch_data), 200


def validate_prelabeled_data(data, log):
    # TODO: IMPLEMENT
    return log


def new_input_batch(session,
                    member,
                    user,
                    project,
                    pre_labeled_data = None,
                    log = regular_log.default()):
    """
        Creates a new comment. At this point we assume data has been validated so no extra checks are
        done to the input data.
    :param session:
    :param log:
    :param member:
    :param project:
    :param discussion:
    :param content:
    :return:
    """

    if pre_labeled_data:
        log = validate_prelabeled_data(pre_labeled_data, log)
        if len(log["error"].keys()) >= 1:
            return False, log

    input_batch = InputBatch.new(
        session = session,
        status = 'pending',
        project_id = project.id,
        member_created_id = member.id,
        memeber_updated_id = member.id,
        pre_labeled_data = pre_labeled_data
    )
    return input_batch.serialize(), log
