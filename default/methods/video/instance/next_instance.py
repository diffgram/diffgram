# OPENCORE - ADD
from methods.regular.regular_api import *

import datetime
from shared.permissions.general import General_permissions
from shared.permissions.super_admin_only import Super_Admin


@routes.route('/api/v1/project/<string:project_string_id>' +
              '/video/<int:video_file_id>/next-instance' +
              '/start/<int:start>',
              methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def next_instance(project_string_id, video_file_id, start       ):
    """
        Jumpst to the next frame where there's an existing instance.
    :return:
    """

    spec_list = [
        {'label_file_id': {
            'required': False,
            'kind': int,

        }}]

    log, input, untrusted_input = regular_input.master(request=request,
                                                       spec_list=spec_list)
    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400

    with sessionMaker.session_scope() as session:
        project = Project.get_by_string_id(session, project_string_id=project_string_id)
        if not project:
            log['error']['project'] = 'Project does not exists.'
            return jsonify(log=log), 400
        next_instance = File.get_next_instance(session=session,
                                               video_parent_file_id=video_file_id,
                                               start_frame_number=start,
                                               label_file_id=input.get('label_file_id'))

        if next_instance:
            return jsonify({'frame_number': next_instance.frame_number}), 200
        else:
            return jsonify({'frame_number': None}), 200
