# OPENCORE - ADD
from methods.regular.regular_api import *
from azure.storage.blob import BlobBlock, BlobServiceClient, ContentSettings, StorageStreamDownloader
from azure.storage.blob._models import BlobSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from shared.helpers import sessionMaker
from shared.database.project import Project
from shared.database.auth.member import Member
from shared.connection.connectors.connectors_base import Connector, with_connection
from methods.input import packet
import threading
import io
import datetime
from pathlib import Path
from methods.export.export_view import export_view_core
from shared.database.export import Export
from methods.export.export_utils import generate_file_name_from_export, check_export_permissions_and_status
import mimetypes

images_allowed_file_names = [".jpg", ".jpeg", ".png"]
videos_allowed_file_names = [".mp4", ".mov", ".avi", ".m4v", ".quicktime"]
allowed_content_types_images = [
    'image/jpeg',
    'image/png',
]
allowed_content_types_videos = [
    'video/mp4',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-m4v',
]


def with_azure_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            return f(*args)
        except Exception as e:
            log['error']['auth_azure_credentials'] = 'Error connecting to Azure Blob Storage. Please ' \
                                                     'check you private secret and id are correct, ' \
                                                     'and that you have the correct pemirssions over your buckets.'
            log['error']['exception_details'] = str(e)
            # return {'log': log}
            raise e

    return wrapper


class AzureConnector(Connector):

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide aws_access_key_id and aws_secret_access_key .'
                return {'log': log}

            self.connection_client = BlobServiceClient.from_connection_string(self.auth_data['client_secret'])

            return {'result': True}
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to Azure. Please check you private key, email and id are correct.'
            return {'log': log}

    @with_connection
    def __fetch_object(self, opts):
        """
        Upload a file to Diffgram from an Azure Blob

        :param opts: Dictionary with parameters for object fetching.
        :return: file obj if file was uploaded, else False
        """
        print('OBJECTCT', opts)
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        shared_access_signature = BlobSharedAccessSignature(
            account_name = self.connection_client.account_name,
            account_key = self.connection_client.credential.account_key
        )

        expiration_offset = 40368000
        blob_name = opts['path']
        container = opts['bucket_name']
        added_seconds = datetime.timedelta(0, expiration_offset)
        expiry_time = datetime.datetime.utcnow() + added_seconds
        filename = blob_name.split("/")[-1]
        sas = shared_access_signature.generate_blob(
            container_name = container,
            blob_name = blob_name,
            start = datetime.datetime.utcnow(),
            expiry = expiry_time,
            permission = BlobSasPermissions(read = True),
            content_disposition = 'attachment; filename=' + filename,
        )
        sas_url = 'https://{}.blob.core.windows.net/{}/{}?{}'.format(
            self.connection_client.account_name,
            container,
            blob_name,
            sas
        )

        with sessionMaker.session_scope() as session:

            project = Project.get_by_string_id(session, self.config_data.get('project_string_id'))
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            # Deduct Media Type:
            extension = Path(opts['path']).suffix
            extension = extension.lower()
            media_type = None
            if extension in images_allowed_file_names:
                media_type = 'image'
            elif extension in videos_allowed_file_names:
                media_type = 'video'
            else:
                # TODO: Decide, do we want to raise an exception? or just do nothing?
                log = regular_log.default()
                log['error']['invalid_type'] = 'File must type of: {} {}'.format(str(images_allowed_file_names),
                                                                                 str(videos_allowed_file_names))
                log['error']['file_name'] = opts['path']
                log['opts'] = opts
                Event.new(
                    session = session,
                    member_id = opts['event_data']['request_user'],
                    kind = 'aws_s3_new_import_warning',
                    description = 'Skipped import for {}, invalid file type.'.format(opts['path']),
                    error_log = log,
                    project_id = project.id,
                    member = member,
                    success = False
                )
                return None

            # metadata = self.connection_client.head_object(Bucket=self.config_data['bucket_name'], Key=path)
            created_input = packet.enqueue_packet(self.config_data['project_string_id'],
                                                  session = session,
                                                  media_url = sas_url,
                                                  media_type = media_type,
                                                  job_id = opts.get('job_id'),
                                                  video_split_duration = opts.get('video_split_duration'),
                                                  directory_id = opts.get('directory_id'))
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session = session,
                member_id = opts['event_data']['request_user'],
                kind = 'aws_s3_new_import_success',
                description = 'New cloud import for {}'.format(opts['path']),
                error_log = opts,
                project_id = project.id,
                member = member,
                success = True
            )
        return created_input

    @with_connection
    def __fetch_folder(self, opts):
        paths = opts['path']
        if type(paths) != list:
            paths = [paths]
        container_client = self.connection_client.get_container_client(container = opts['bucket_name'])
        for current_path in paths:
            files = container_client.list_blobs(name_starts_with = current_path)
            for file in files:
                if not file.name.endswith('/'):
                    opts_fetch_object = {}
                    opts_fetch_object.update(opts)

                    new_opts = {
                        'path': file.name,
                        'directory_id': opts.get('directory_id'),
                        'bucket_name': opts.get('bucket_name'),
                    }
                    print('asdasd', new_opts)
                    opts_fetch_object.update(new_opts)
                    self.__fetch_object(opts_fetch_object)

    @with_connection
    @with_azure_exception_handler
    def __start_folder_fetch(self, opts):

        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        t = threading.Thread(
            target = self.__fetch_folder,
            args = ((opts,)))
        t.start()
        return {'result': True}

    @with_connection
    @with_azure_exception_handler
    def __list_container_directories(self, opts):
        keys = []
        container_client = self.connection_client.get_container_client(container = opts['bucket_name'])
        for file in container_client.walk_blobs(name_starts_with = opts['path'], delimiter = '/'):
            if file.name.endswith('/'):
                keys.append(file.name)
        return keys

    @with_connection
    @with_azure_exception_handler
    def __list_container_files(self, opts):
        container_client = self.connection_client.get_container_client(container = opts['bucket_name'])
        blobs = container_client.walk_blobs(name_starts_with = opts['path'])
        keys = []
        for blob in list(blobs):
            if blob.name.endswith('/'):
                continue
            if not blob.name.startswith(opts['path']) and '/' in blob.name:
                continue
            keys.append(blob.name)
        return keys

    @with_connection
    @with_azure_exception_handler
    def __get_folder_contents(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        prefix = opts['path']
        just_folders = opts.get('just_folders', False)
        files = []
        if not just_folders:
            files = sorted(self.__list_container_files(opts))
        folders = sorted(list(self.__list_container_directories(opts)))

        result = folders + files
        return {'result': result}

    @with_connection
    @with_azure_exception_handler
    def __list_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        blob_client = self.connection_client.get_blob_client(container = input['bucket_name'])
        blobs = blob_client.list_blobs(starts_with = opts['path'])
        keys = []
        for blob in blobs:
            keys.append(blob.name)
        return {'result': keys}

    @with_connection
    @with_azure_exception_handler
    def __count_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        count = 0
        blob_client = self.connection_client.get_blob_client(container = input['bucket_name'])
        blobs = blob_client.list_blobs(starts_with = opts['path'])
        count = len(blobs)
        return {'result': count}

    @with_connection
    @with_azure_exception_handler
    def __list_buckets(self, opts):
        """
            List all the buckets/containers on the Azure blob storage account.
        :param opts:
        :return:
        """
        result = []
        containers = self.connection_client.list_containers()
        for container in containers:
            result.append(container.name)
        return {'result': result}

    @with_azure_exception_handler
    def __send_export(self, opts):
        spec_list = [{'project_string_id': dict}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = self.config_data,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        spec_list = [
            {'path': str},
            {"format": {
                'default': 'JSON',
                'kind': str,
                'valid_values_list': ['JSON', 'YAML']
            }},
            {'export_id': str},
            {'bucket_name': str},

        ]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log,
                                                    string_len_not_zero = False)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        if not opts['path'].endswith('/') and opts['path'] != '':
            log['error']['path'] = 'Path on bucket must be a folder, not a filename.'
            return log

        with sessionMaker.session_scope() as session:
            project = Project.get_by_string_id(session, self.config_data['project_string_id'])
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            export = session.query(Export).filter(Export.id == opts['export_id']).first()
            # Check perms and export status.
            export_check_result = check_export_permissions_and_status(export,
                                                                      self.config_data['project_string_id'],
                                                                      session)
            if len(export_check_result['error'].keys()) > 1:
                return export_check_result

            result = export_view_core(
                export = export,
                format = opts['format'],
                return_type = 'bytes')
            filename = generate_file_name_from_export(export, session)

            if opts['path'] != '':
                key = '{}{}.{}'.format(opts['path'], filename, opts['format'].lower())
            else:
                key = '{}.{}'.format(filename, opts['format'].lower())

            file = io.BytesIO(result)
            blob_client = self.azure_service_client.get_blob_client(container = opts['bucket_name'], blob = key)
            content_type = mimetypes.guess_type(input.original_filename)[0]
            my_content_settings = ContentSettings(content_type = content_type)
            blob_client.upload_blob(file, content_settings = my_content_settings)
            blob_client.upload_fileobj(file, opts['bucket_name'], key)

            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session = session,
                member_id = opts['event_data']['request_user'],
                kind = 'aws_s3_new_export_success',
                description = 'New cloud export for {}{}'.format(opts['path'], filename),
                error_log = opts,
                member = member,
                project_id = project.id,
                success = True
            )
            return {'result': True}

    def test_connection(self):
        auth_result = self.connect()
        if 'log' in auth_result:
            return auth_result
        # Test fecthing buckets
        result_buckets = self.__list_buckets({})
        if 'log' in result_buckets:
            return result_buckets
        return result_buckets

    @with_connection
    def get_meta_data(self):
        return {}

    @with_connection
    def fetch_data(self, opts):
        """
            This function routes any action_type to the correct S3 connector actions.
        :return: Object
        """
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'fetch_object':
            return self.__fetch_object(opts)
        if action_type == 'list_objects':
            return self.__fetch_object(opts)
        if action_type == 'count_objects':
            return self.__count_objects(opts)
        if action_type == 'fetch_folder':
            return self.__start_folder_fetch(opts)
        if action_type == 'list_buckets':
            return self.__list_buckets(opts)
        if action_type == 'get_folder_contents':
            return self.__get_folder_contents(opts)

    @with_connection
    def put_data(self, opts):
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'send_export':
            return self.__send_export(opts)
