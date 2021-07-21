# OPENCORE - ADD
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.database.batch.batch import InputBatch
import os
import tempfile
from werkzeug.utils import secure_filename
from shared.data_tools_core import Data_tools

data_tools = Data_tools().data_tools


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


def save_pre_labeled_data_to_db():
    """
        Gets the prelabeled data from the cloud URL and sets it in the
        corresponding DB row.
        
    :return:
    """


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
    raise Exception('Random error')
    content_range = request.headers.get('Content-Range')
    content_range_index = int(request.headers.get('Content-Range-Index'))
    total_chunks = int(request.headers.get('Content-Range-Total-Chunks'))
    if content_range.startswith('bytes'):
        new_range = content_range.replace('bytes ', '')
        chunks = new_range.split('/')[0]
        size = int(new_range.split('/')[1])
        chunk_start = int(new_range.split('-')[0])
        chunk_end = int(chunks.split('-')[1])
        temp_dir_path = '/tmp/batches/{}_batch_payload.json'.format(batch.id)
        if chunk_start == 0:
            session.add(batch)
            url = data_tools.create_resumable_upload_session(
                blob_path = temp_dir_path,
                content_type = 'application/json',
                input = None
            )
            batch.data_temp_dir = url
            session.add(batch)
            stream = file.stream.read()
            content_size = len(stream)

            response = data_tools.transmit_chunk_of_resumable_upload(
                stream = stream,
                blob_path = temp_dir_path,
                content_type = 'application/json',
                prior_created_url = batch.data_temp_dir,
                content_start = chunk_start,
                content_size = content_size,
                total_size = size,
                total_parts_count = total_chunks,
                chunk_index = content_range_index,
                input = None,
                batch = batch,
            )
        else:
            stream = file.stream.read()
            content_size = len(stream)

            response = data_tools.transmit_chunk_of_resumable_upload(
                stream = stream,
                blob_path = temp_dir_path,
                content_type = 'application/json',
                prior_created_url = batch.data_temp_dir,
                content_start = chunk_start,
                content_size = content_size,
                total_size = size,
                total_parts_count = total_chunks,
                chunk_index = content_range_index,
                input = None,
                batch = batch,
            )

        session.add(batch)
        if chunk_end == (size - 1):
            # Get the complete file and write it to the input batch.
            batch.data_temp_dir = temp_dir_path
            batch.pre_labeled_data = None
            session.add(batch)
            result = batch.get_pre_labeled_data_cloud_url()
            t = threading.Thread(
                target = save_pre_labeled_data_to_db(),
                args = ((opts,)))
            t.start()
    else:
        log['error']['content_range'] = 'Invalid content range header.'
        return False, log

    return result, log
