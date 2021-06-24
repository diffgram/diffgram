# OPENCORE - ADD
from methods.regular.regular_api import *
import os
import tempfile
from werkzeug.utils import secure_filename
# not needed now, as we don't call directly
from methods.input.process_media import Process_Media

from methods.input.process_media import PrioritizedItem
from methods.input.process_media import add_item_to_queue

from shared.database.input import Input
from shared.database.batch.batch import InputBatch

from shared.data_tools_core import Data_tools
from shared.database.source_control.file import File

data_tools = Data_tools().data_tools


@routes.route('/api/walrus/project/<string:project_string_id>/upload/large',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=['admin', "Editor"],
    apis_user_list=['api_enabled_builder',
                    'security_email_verified'])
@limiter.limit("4 per second")
def api_project_upload_large(project_string_id):
    """
    Error handling: Do we want a pattern of looking at logs
        or the input item... depends maybe both depends on context
    """

    with sessionMaker.session_scope() as session:

        project = Project.get(session, project_string_id)

        upload = Upload(
            session=session,
            project=project,
            request=request)

        upload.route_from_unique_id()
        if len(upload.log["error"].keys()) >= 1:
            return jsonify(log=upload.log), 400

        upload.process_chunk(
            request=upload.request,
            input=upload.input)

        if len(upload.log["error"].keys()) >= 1:
            return jsonify(log=upload.log), 400

        more_chunks_expected: bool = int(upload.dzchunkindex) + 1 != int(upload.dztotalchunkcount)

        if more_chunks_expected is False:
            upload.start_media_processing(input=upload.input)

        return jsonify(success=True), 200


class Upload():

    def __init__(self,
                 session,
                 project,
                 request):

        self.session = session
        self.project = project
        self.request = request
        self.log = regular_log.default()

    def get_project_labels(self):
        result = []
        directory = self.project.directory_default

        working_dir_sub_query = self.session.query(WorkingDirFileLink).filter(
            WorkingDirFileLink.working_dir_id == directory.id,
            WorkingDirFileLink.type == "label").subquery('working_dir_sub_query')

        working_dir_file_list = self.session.query(File).filter(
            File.id == working_dir_sub_query.c.file_id).all()

        for file in working_dir_file_list:
            if file.state != "removed":
                result.append(file.serialize_with_label_and_colour(session = self.session))
        return result

    def extract_instance_list_from_batch(self, input, input_batch_id, file_name):
        input_batch = InputBatch.get_by_id(self.session, id=input_batch_id)
        pre_labels = input_batch.pre_labeled_data
        if pre_labels is None:
            return input
        uuid = None
        file_data = None
        if self.request:
            uuid = self.request.form.get('uuid')
            file_data = pre_labels.get(uuid)
        if file_data is None:
            # Try finding the pre_labels with the file_name as a backup
            file_data = pre_labels.get(file_name)
            if file_data is None:
                logger.warning('Input: {} File {} has no pre_labeled data associated'.format(input.id, file_name))
                return
        project_labels = self.get_project_labels()

        if file_data['instance_list']:
            instance_list = file_data['instance_list']
            for instance in instance_list:
                label_file = list(filter(lambda x: x['label']['name'] == instance['name'], project_labels))[0]
                instance['label_file_id'] = label_file['id']
            input.instance_list = {'list': file_data['instance_list']}

        if file_data['frame_packet_map']:
            frame_packet_map = file_data['frame_packet_map']
            for frame, instance_list in frame_packet_map.items():
                for instance in instance_list:
                    label_file = list(filter(lambda x: x['label']['name'] == instance['name'], project_labels))[0]
                    instance['label_file_id'] = label_file['id']
            input.frame_packet_map = frame_packet_map
        return input

    def route_from_unique_id(self):
        """
        This is fairly heavily tied to dropzone still
        but in theory could abstract it to a generic unique upload id

        Not 100% sure on trade offs of doing it throught
        self vs passing request etc...
        Perhaps is nice pattern to start thinking more in terms of external
        objects like  upload.attribute instead of self.attribute.
        """

        self.binary_file = self.request.files.get('file')
        # to distinguish from diffgram file which we normally just call 'file'
        if not self.binary_file:
            self.log['error']['binary_file'] = "No file provided"
            return

        self.load_drop_zone_info(request=self.request)

        self.is_first_chunk: bool = self.dzchunkindex == 0

        if self.is_first_chunk is True:
            self.create_input(
                project=self.project,
                request=self.request,
                filename=self.binary_file.filename)
        else:
            self.input = self.session.query(Input).filter(
                Input.dzuuid == self.dzuuid,
                Input.project == self.project).first()

            self.session.add(self.input)  # for various status updates

        # TODO handle if self.input is None.

    def load_drop_zone_info(self, request):
        """
        Reminder it's easier to look at front
        end dev tools > network > headers > form data
        when sending a request. (3rd party library, so it's a bit of discovery thing)

        https://www.dropzonejs.com/#configuration
        Names don't exactly match... it seems to add the "dz" thing there
        """

        self.dzuuid = request.form.get('dzuuid', None)
        self.dzchunksize = request.form.get('dzchunksize', None)
        self.dztotalchunkcount = request.form.get('dztotalchunkcount', None)
        try:
            self.dzchunkbyteoffset = int(request.form.get('dzchunkbyteoffset', None))
            self.dzchunkindex = int(request.form.get('dzchunkindex', None))
            self.dztotalfilesize = int(request.form.get('dztotalfilesize', None))
        except Exception as exception:
            self.log['error']['dzinfo'] = str(exception)
            return

    def start_media_processing(self, input):
        """
        In context of having a completed file
        Start actual media processing
        (Rest of "processing" here generally refers to binary
        data)

        note we close the session usually in this context
        so we pass input ID instead of input object
        """

        item = PrioritizedItem(
            priority=100,
            media_type=input.media_type,  # For routing to right queue
            input_id=input.id)

        add_item_to_queue(item)

        user = User.get(session=self.session)

        Event.new(
            session=self.session,
            kind="input_from_upload_UI",
            member_id=user.member_id,
            success=True,
            project_id=self.project.id,
            description=str(input.media_type) + " " + str(self.project.project_string_id),
            input_id=input.id
        )

    def process_chunk(self, request, input):
        """
        Not 100% sure on where the try blocks should be used
        in this case... or how we want to handle response errors
        on requests.put() side.
        """

        stream = self.binary_file.stream.read()
        content_size = len(stream)

        try:
            response = data_tools.transmit_chunk_of_resumable_upload(
                stream=stream,
                blob_path=input.raw_data_blob_path,
                prior_created_url=input.resumable_url,
                content_type=None,
                content_start=self.dzchunkbyteoffset,
                content_size=content_size,
                total_size=self.dztotalfilesize,
                total_parts_count=self.dztotalchunkcount,
                chunk_index=self.dzchunkindex,
                input = self.input,
            )
            if response is False:
                input.status = "failed"
                input.status_text = "Please try again, or try using API/SDK. (Raw upload error)"
                return

        except Exception as exception:
            input.status = "failed"
            input.status_text = "Please try again, or try using API/SDK. (Raw upload error)"
            raise Exception #TODO REMOVE

    @staticmethod
    def upload_limits(input,
                      file_size,
                      file_size_limit: int = 5 * 1024 * 1024 * 1024):
        """
        Future could also get this from blob maybe
        since someone could fake drop zone thing...

        For now storing this as a status text thing...
        but could alternatively log as error and return

        """

        if file_size > file_size_limit:
            input.status = "failed"
            input.status_text = "Exceeded max file size"

        return input

    def create_input(
            self,
            project,
            request,
            filename
    ):

        self.input = Input.new(
            project=project,
            media_type=None,
            job_id=request.form.get('job_id'),
            type=request.form.get('source', 'from_resumable'),
            directory_id=request.form.get('directory_id'),  # Not trusted
            video_split_duration=request.form.get('video_split_duration'),
            batch_id=request.form.get('input_batch_id')
        )

        self.extract_instance_list_from_batch(self.input, input_batch_id = request.form.get('input_batch_id'), file_name = filename)

        self.session.add(self.input)

        self.input = Upload.upload_limits(
            input=self.input,
            file_size=self.dztotalfilesize)

        self.input.original_filename = secure_filename(
            filename)  # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        self.input.extension = os.path.splitext(self.input.original_filename)[1].lower()
        self.input.original_filename = os.path.split(self.input.original_filename)[1]

        # At somepoint should really declare
        # From UI here...
        self.input.dzuuid = self.dzuuid
        self.input.action_flow_id = request.headers.get('flow_id')

        if self.input.action_flow_id:

            if self.input.flow is None:
                self.input.status = "failed"
                self.input.status_text = "No flow found"
                return

        self.input.mode = request.headers.get('mode')

        self.input.media_type = Process_Media.determine_media_type(
            extension=self.input.extension)

        if not self.input.media_type:
            self.input.status = "failed"
            self.input.status_text = "Invalid file type: " + self.input.extension

        # self.input.user =

        self.session.flush()  # For ID for path

        self.input.raw_data_blob_path = settings.PROJECT_RAW_IMPORT_BASE_DIR + \
                                        str(self.input.project.id) + "/raw/" + str(self.input.id)

        data_tools.create_resumable_upload_session(
            blob_path=self.input.raw_data_blob_path,
            content_type=None,
            input = self.input
        )



@routes.route('/api/walrus/v1/project/<string:project_string_id>/input/from_local',
              methods=['POST'])
@Project_permissions.user_has_project(
    Roles=['admin', "Editor"],
    apis_user_list=['api_enabled_builder',
                    'security_email_verified'])
@limiter.limit("1 per second, 5000 per day")
def api_project_input_from_local(project_string_id):

    try:
        json_parsed = json.loads(request.form.get('json'))
    except:
        temp_log = regular_log.default_api_log()
        temp_log["error"]["input"] = "Expecting a key 'json' in form request."
        return jsonify(log=temp_log), 400

    spec_list = [{"instance_list": {
                     'default': None,
                     'kind': list,
                     'allow_empty': True,
                     'required': False
                    }
                 },
                 {"frame_packet_map": {     # WIP
                     'default': None,
                     'kind': dict,
                     'required': False
                    }
                 }
                 ]

    log, input, untrusted_input = regular_input.master(
        request=request,
        spec_list=spec_list,
        untrusted_input=json_parsed)

    if len(log["error"].keys()) >= 1:
        return jsonify(log=log), 400


    with sessionMaker.session_scope() as session:

        directory_id = request.headers.get('directory_id')

        file = request.files.get('file')
        if not file:
            log['error'] = "No files"
            return False, log, None

        result, log, input = input_from_local(
            session=session,
            log=log,
            project_string_id=project_string_id,
            file=file,
            directory_id = directory_id,
            http_input = input)

        if result is not True:
            return jsonify(
                log=log,
                input=input.serialize()), 400

        if result is True:
            log['success'] = True
            return jsonify(
                log=log,
                input=input.serialize(),
                file=input.file.serialize()), 200



def input_from_local(session,
                     log,
                     project_string_id,
                     http_input,
                     file,
                     directory_id):
    # TODO review how we want to handle header options
    # Especially if needs to be outside of function for python requests...
    # immediate_mode = request.headers['immediate_mode']
    # Issues to be careful with ie string treamtment of 'True' vs True...
    immediate_mode = True


    input = Input()
    input.directory_id = directory_id

    if http_input['instance_list']:
        input.instance_list = {}
        input.instance_list['list'] = http_input['instance_list']

    if http_input['frame_packet_map']:
        input.frame_packet_map = http_input['frame_packet_map']

    # only need to make temp dir if file doesn't already exist...

    original_filename = secure_filename(file.filename)  # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

    input.extension = os.path.splitext(original_filename)[1].lower()
    input.original_filename = os.path.split(original_filename)[1]

    input.temp_dir = tempfile.mkdtemp()
    input.temp_dir_path_and_filename = input.temp_dir + \
                                       "/" + original_filename + input.extension

    project = Project.get(session, project_string_id)

    input.project = project

    input.media_type = None
    input.media_type = Process_Media.determine_media_type(input.extension)
    if not input.media_type:
        input.status = "failed"
        input.status_text = "Invalid file type: " + input.extension
        return False, log, input

    session.add(input)
    session.flush()

    with open(input.temp_dir_path_and_filename, "wb") as f:

        f.write(file.stream.read())

    # For LOCAL not normal upload
    file_size_limit = 9 * 1024 * 1024 * 1024

    file_size = os.path.getsize(input.temp_dir_path_and_filename)  # gets size in bytes

    if file_size > file_size_limit:
        input.status = "failed"
        input.status_text = "Exceeded max file size"
        return False, log, input

    if immediate_mode == True or immediate_mode is None:
        # Leave this as a direct call for time being, as we pass
        # the input back to thing on front end

        process_media = Process_Media(
            session=session,
            input=input)

        result = process_media.main_entry()

        # Always return input along with file?

        if result == True:
            return True, log, input

        if result == False:
            return False, log, input

    # Default
    priority = 100

    item = PrioritizedItem(
        priority=priority,
        input_id=input.id,
        media_type=input.media_type
    )

    add_item_to_queue(item)

    return True, log, input
