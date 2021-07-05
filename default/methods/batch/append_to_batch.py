# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.batch.batch import InputBatch
import os
import tempfile
from werkzeug.utils import secure_filename


@routes.route('/api/v1/project/<string:project_string_id>/input-batch/<int:batch_id>/append-data',
              methods = ['POST'])
@Project_permissions.user_has_project(Roles = ["admin", "Editor"], apis_user_list = ["api_enabled_builder"])
def append_to_batch_api(project_string_id, batch_id):
    """
        Create a new input Batch to attach inputs to it later.
    :param project_string_id:
    :param discussion_id:
    :return:
    """
    with sessionMaker.session_scope() as session:

        project = Project.get_by_string_id(session, project_string_id)
        user = User.get(session)

        if user:
            member = user.member
        else:
            client_id = request.authorization.get('username', None)
            auth = Auth_api.get(session, client_id)
            member = auth.member

        batch_data, log = append_to_batch_core(
            session = session,
            batch_id = batch_id,
            log = regular_log.default(),
            member = member,
            project = project,
            request = request,
        )
        if len(log["error"].keys()) >= 1:
            return jsonify(log = log), 400

        return jsonify(input_batch = batch_data), 200


def append_to_batch_core(session, log, batch_id, member, project, request):
    result = None
    batch = InputBatch.get_by_id(session = session, id = batch_id)

    if batch.project_id != project.id:
        log['error']['batch_id'] = "Batch is not from the provided project."
        return False, log

    binary_file = request.files.get('file')
    if not binary_file:
        log['error']['binary_file'] = "No file provided"
        return False, log

    file = request.files['file']
    # secure_filename makes sure the filename isn't unsafe to save

    content_range = request.headers.get('Content-Range')
    if content_range.startswith('bytes'):
        new_range = content_range.replace('bytes ', '')
        chunks = new_range.split('/')[0]
        size = int(new_range.split('/')[1])
        chunk_start = int(new_range.split('-')[0])
        chunk_end = int(chunks.split('-')[1])
        if chunk_start == 0:
            temp_dir = tempfile.mkdtemp()
            batch.data_temp_dir = temp_dir
            session.add(batch)
            save_path = os.path.join(temp_dir, secure_filename('{}_batch_payload.json'.format(batch.id)))
        else:
            save_path = os.path.join(batch.data_temp_dir, secure_filename('{}_batch_payload.json'.format(batch.id)))

        # We need to append to the file, and write as bytes
        with open(save_path, 'ab') as f:
            # Goto the offset, aka after the chunks we already wrote
            f.seek(chunk_start)
            f.write(file.stream.read())
        if chunk_end == (size - 1):
            # Get the complete file and write it to the input batch.
            with open(save_path, 'r') as f:
                # Goto the offset, aka after the chunks we already wrote
                data = json.load(f)
                batch.pre_labeled_data = data
                session.add(batch)
    else:
        log['error']['content_range'] = 'Invalid content range header.'
        return False, log

    return result, log
