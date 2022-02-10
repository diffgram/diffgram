# OPENCORE - ADD
import requests
import time
import threading
import logging
import traceback

from shared.connection.connectors.connectors_base import Connector, with_connection
from google.cloud import storage
from google.oauth2 import service_account
from shared.helpers import sessionMaker
from methods.input import packet
from pathlib import Path
from shared.regular import regular_input
from shared.regular import regular_log
from methods.export.export_view import export_view_core
from shared.database.export import Export
from methods.export.export_utils import generate_file_name_from_export, check_export_permissions_and_status
from shared.database.project import Project
from shared.database.event.event import Event
from shared.database.auth.member import Member


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


def with_google_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            res = f(*args)
            return res
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to google cloud storage. Please check you private key, email and id are correct.'
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class GoogleCloudStorageConnector(Connector):

    def generate_auth_data(
            self,
            email: str,
            client_id,
            client_secret,
            project_id):
        return {
            'client_email': email,
            'private_key_id': client_id,
            'private_key': client_secret.replace('\\n', '\n'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            'project_id': project_id
        }

    @with_google_exception_handler
    def connect(self):
        log = regular_log.default()
        if 'project_id' not in self.auth_data or \
                (self.auth_data['project_id'] is '' or self.auth_data['project_id'] is None):
            log['error']['client_project'] = "ValueError: Client project not set: pass an explicit project."
            return {'log': log}

        auth = self.generate_auth_data(
            email=self.auth_data['client_email'],
            client_id=self.auth_data['client_id'],
            client_secret=self.auth_data['client_secret'],
            project_id=self.auth_data['project_id'])

        credentials = service_account.Credentials.from_service_account_info(auth)
        self.connection_client = storage.Client(credentials=credentials, project=auth['project_id'])

        return {'result': True}

    @with_connection
    @with_google_exception_handler
    def __list_gcs_directories(self, opts):
        prefix = opts['path']
        bucket_name = opts['bucket_name']
        # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920
        bucket = self.connection_client.get_bucket(bucket_name)
        iterator = bucket.list_blobs(prefix=prefix, delimiter='/')
        prefixes = set()
        count = 0
        for page in iterator.pages:
            if count > 5000:
                break
            prefixes.update(page.prefixes)
            count += 1
        return prefixes

    @with_connection
    @with_google_exception_handler
    def __list_gcs_files(self, opts):
        prefix = opts['path']
        bucket_name = opts['bucket_name']
        # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920fp
        bucket = self.connection_client.get_bucket(bucket_name)
        iterator = bucket.list_blobs(prefix=prefix, delimiter='/')
        result = []
        count = 0
        for blob in iterator:
            if count > 5000:
                break
            if blob.name != opts['path']:
                result.append(blob.name)
            count += 1

        return result

    @with_connection
    @with_google_exception_handler
    def __get_folder_contents(self, opts):
        just_folders = opts.get('just_folders', False)
        files = []
        if not just_folders:
            files = sorted(self.__list_gcs_files(opts))
        folders = sorted(list(self.__list_gcs_directories(opts)))
        result = folders + files
        return {'result': result}

    @with_connection
    @with_google_exception_handler
    def __list_buckets(self, opts):
        buckets = self.connection_client.list_buckets()
        return {'result': [b.name for b in buckets]}

    @with_connection
    @with_google_exception_handler
    def __fetch_object(self, opts):
        bucket = self.connection_client.get_bucket(opts['bucket_name'])
        blob = bucket.blob(opts['path'])
        blob_expiry = int(time.time() + (60 * 60 * 24 * 30))
        signed_url = blob.generate_signed_url(expiration=blob_expiry)
        # Deduct Media Type:
        # TODO Share this with existing process_media determine_media_type()
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
            with sessionMaker.session_scope() as session:
                Event.new(
                    session=session,
                    member_id=opts['event_data']['request_user'],
                    kind='google_cloud_new_import_error',
                    description='New cloud import for {}'.format(opts['path']),
                    error_log=log
                )
            raise LookupError(
                'File must type of: {} {}'.format(str(images_allowed_file_names), str(videos_allowed_file_names)))
        # metadata = self.connection_client.head_object(Bucket=opts['bucket_name, Key=path)
        with sessionMaker.session_scope() as session:
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            created_input = packet.enqueue_packet(self.config_data['project_string_id'],
                                                  session=session,
                                                  media_url=signed_url,
                                                  media_type=media_type,
                                                  job_id=opts.get('job_id'),
                                                  video_split_duration=opts.get('video_split_duration'),
                                                  directory_id=opts.get('directory_id'),
                                                  member = member)
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session=session,
                member_id=opts['event_data']['request_user'],
                kind='google_cloud_new_import_success',
                description='New cloud import for {}'.format(opts['path']),
                error_log=opts
            )
        return {'result': created_input}

    @with_connection
    @with_google_exception_handler
    def __get_string_data(self, opts):
        # get bucket with name
        bucket = self.connection_client.get_bucket(opts['bucket_name'])
        blob = bucket.blob(opts['path'])
        # download as string
        str_value = blob.download_as_string().decode("utf-8")
        return {'data': str_value}

    @with_connection
    @with_google_exception_handler
    def __list_objects(self, opts):
        blobs = self.connection_client.list_blobs(opts['bucket_name'], prefix=opts['path'])
        return {'result': [x.name for x in blobs]}

    @with_connection
    @with_google_exception_handler
    def __count_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}

        blobs = self.connection_client.list_blobs(opts['bucket_name'], prefix=opts['path'])
        count = 0
        for b in blobs:
            if b.name.endswith('/'):
                continue
            count += 1
        return {'result': count}

    @with_connection
    def __fetch_folder(self, opts):
        result = []

        if self.config_data.get('project_string_id') is None:
            return {'result': 'error'}
        paths = opts['path']
        if type(paths) != list:
            paths = [paths]
        with sessionMaker.session_scope() as session:
            project = Project.get_by_string_id(session, self.config_data.get('project_string_id'))
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            for path in paths:
                blobs = self.connection_client.list_blobs(opts['bucket_name'], prefix=path)
                for blob in blobs:
                    # Deduct Media Type:
                    if blob.name.endswith('/'):
                        continue

                    blob_expiry = int(time.time() + (60 * 60 * 24 * 30))
                    signed_url = blob.generate_signed_url(expiration=blob_expiry)
                    extension = Path(blob.path).suffix
                    media_type = None
                    if extension in images_allowed_file_names:
                        media_type = 'image'
                    elif extension in videos_allowed_file_names:
                        media_type = 'video'
                    else:
                        logging.warn('File: {} must type of: {} {}'.format(
                            blob.name,
                            str(images_allowed_file_names),
                            str(videos_allowed_file_names)))

                        log = regular_log.default()
                        log['error']['invalid_type'] = 'File must type of: {} {}'.format(str(images_allowed_file_names),
                                                                                         str(videos_allowed_file_names))
                        log['error']['file_name'] = path
                        log['opts'] = opts
                        Event.new(
                            session=session,
                            member_id=opts['event_data']['request_user'],
                            kind='google_cloud_new_import_warning',
                            description='Skipped import for {}, invalid file type.'.format(blob.name),
                            error_log=log,
                            project_id=project.id,
                            member=member,
                            success=False
                        )
                        continue
                    result = []
                    # TODO: check Input() table for duplicate file?
                    member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
                    created_input = packet.enqueue_packet(self.config_data['project_string_id'],
                                                          session=session,
                                                          media_url=signed_url,
                                                          media_type=media_type,
                                                          job_id=opts.get('job_id'),
                                                          batch_id=opts.get('batch_id'),
                                                          file_name=path,
                                                          video_split_duration=opts.get('video_split_duration'),
                                                          directory_id=opts.get('directory_id'),
                                                          extract_labels_from_batch = True,
                                                          member = member)
                    log = regular_log.default()
                    log['opts'] = opts
                    Event.new(
                        session=session,
                        member_id=opts['event_data']['request_user'],
                        kind='google_cloud_new_import_success',
                        description='New cloud import for {}'.format(blob.name),
                        error_log=opts,
                        project_id=project.id,
                        member=member,
                        success=True
                    )
                    result.append(created_input)
        return result

    @with_connection
    @with_google_exception_handler
    def __start_fetch_folder(self, opts):
        spec_list = [{'project_string_id': dict}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=self.config_data,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}

        t = threading.Thread(
            target=self.__fetch_folder,
            args=((opts,)))
        t.start()
        return {'result': True}

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
        if action_type == 'get_string_data':
            return self.__get_string_data(opts)
        if action_type == 'list_objects':
            return self.__list_objects(opts)
        if action_type == 'count_objects':
            return self.__count_objects(opts)
        if action_type == 'fetch_folder':
            return self.__start_fetch_folder(opts)
        if action_type == 'get_folder_contents':
            return self.__get_folder_contents(opts)
        if action_type == 'list_buckets':
            return self.__list_buckets(opts)

    @with_connection
    @with_google_exception_handler
    def __send_export(self, opts):
        spec_list = [{'project_string_id': dict}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=self.config_data,
                                                    spec_list=spec_list,
                                                    log=log)
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
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log,
                                                    string_len_not_zero=False)
        if len(log["error"].keys()) >= 1:
            return {'log': log}

        if not opts['path'].endswith('/') and opts['path'] != '':
            log['error']['path'] = 'Path on bucket must be a folder, not a filename.'
            return {'log': log}

        with sessionMaker.session_scope() as session:
            project = Project.get_by_string_id(session, self.config_data['project_string_id'])
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            export = session.query(Export).filter(Export.id == opts['export_id']).first()
            # Check perms and export status.
            export_check_result = check_export_permissions_and_status(export,
                                                                      self.config_data['project_string_id'],
                                                                      session)
            if regular_log.log_has_error(export_check_result):
                log = regular_log.default()
                log['error'] = export_check_result['error']
                log['error']['file_name'] = opts['path']
                log['opts'] = opts
                Event.new(
                    session=session,
                    member_id=opts['event_data']['request_user'],
                    kind='google_cloud_new_export_error',
                    description='Google cloud export error for {}'.format(opts['path']),
                    error_log=log,
                    member=member,
                    project_id=project.id,
                    success=False
                )
                return export_check_result

            bucket = self.connection_client.get_bucket(opts['bucket_name'])
            result = export_view_core(
                export=export,
                format=opts['format'],
                return_type='bytes')
            filename = generate_file_name_from_export(export, session)

            if opts['path'] != '':
                blob = bucket.blob('{}{}.{}'.format(opts['path'], filename, opts['format'].lower()))
            else:
                blob = bucket.blob('{}.{}'.format(filename, opts['format'].lower()))
            blob.upload_from_string(result)
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session=session,
                member_id=opts['event_data']['request_user'],
                kind='google_cloud_new_export_success',
                description='New cloud export for {}'.format(blob.name),
                error_log=opts,
                member=member,
                project_id=project.id,
                success=True
            )
            return {'result': True}

    @with_connection
    def put_data(self, opts):
        """
            This function routes any action_type to the correct S3 connector actions.
        :return: Object
        """
        action_type = opts.pop('action_type')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        if action_type == 'send_export':
            return self.__send_export(opts)
        raise NotImplementedError

    @with_connection
    def get_meta_data(self):
        raise NotImplementedError

    def validate_gcp_connection_read_write(self, bucket_name):
        test_file_path = 'diffgram_test_file.txt'
        log = regular_log.default()
        try:
            bucket = self.connection_client.get_bucket(bucket_name)
            blob = bucket.blob(test_file_path)
            blob.upload_from_string('This is a diffgram test file', content_type = 'text/plain')
        except Exception as e:
            log['error']['gcp_write_perms'] = 'Error Connecting to GCP: Please check you have write permissions on the GCP bucket.'
            log['error']['details'] = traceback.format_exc()
            return False, log
        try:
            expiration_offset = 40368000
            expiration_time = int(time.time() + expiration_offset)
            bucket.blob(test_file_path)

            filename = test_file_path.split("/")[-1]
            url_signed = blob.generate_signed_url(
                expiration = expiration_time,
                response_disposition = 'attachment; filename=' + filename
            )
            resp = requests.get(url_signed)
            if resp.status_code != 200:
                raise Exception(
                    'Error when accessing presigned URL: Status({}). Error: {}'.format(resp.status_code, resp.text))
        except:
            log['error']['gcp_write_perms'] = 'Error Connecting to GCP: Please check you have read permissions on the GCP bucket.'
            log['error']['details'] = traceback.format_exc()
            return False, log
        return True, log

    def test_connection(self):
        auth_result = self.connect()
        if 'log' in auth_result:
            return auth_result
        # Test fecthing buckets
        result_buckets = self.__list_buckets({})
        bucket_names = result_buckets.get('result')

        if 'log' in result_buckets:
            return result_buckets

        if bucket_names and  len(bucket_names) > 0:
            validation_result, log = self.validate_gcp_connection_read_write(bucket_names[0])
            if len(log['error'].keys()) > 0:
                return {'log': log}


        return result_buckets
