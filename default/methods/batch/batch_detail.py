# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.batch.batch import InputBatch


@routes.route('/api/v1/project/<string:project_string_id>/input-batch/<int:batch_id>',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def input_batch_detail_api(project_string_id, batch_id):
    """
        Get the input batch ID details
    :param project_string_id:
    :param batch_id:
    :return:
    """
    input_batch_spec_list = []

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

        batch_data, log = input_batch_detail_core(
            session = session,
            log = log,
            member = member,
            project = project,
            user = user,
            batch_id = batch_id
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(input_batch = batch_data), 200


def input_batch_detail_core(session,
                            member,
                            user,
                            project,
                            batch_id,
                            log = regular_log.default()):
    """
        Returns a dictionary with the input batch data
    :param session:
    :param log:
    :param member:
    :param user:
    :param project:
    :param batch_id:
    :param log:
    :return:
    """

    input_batch = InputBatch.get_by_id(
        session = session,
        id = batch_id
    )

    return input_batch.serialize(), log
