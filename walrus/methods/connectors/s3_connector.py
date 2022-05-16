# OPENCORE - ADD
import boto3
import traceback
import threading
import io
import requests

from methods.regular.regular_api import *
from shared.helpers import sessionMaker
from shared.database.project import Project
from shared.database.auth.member import Member
from shared.connection.connectors.connectors_base import Connector, with_connection
from methods.input import packet
from pathlib import Path
from methods.export.export_view import export_view_core
from shared.database.export import Export
from methods.export.export_utils import generate_file_name_from_export, check_export_permissions_and_status
from shared.regular import regular_log

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


def with_s3_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            return f(*args)
        except Exception as e:
            log['error']['auth_s3_credentials'] = 'Error connecting to AWS S3. Please ' \
                                                  'check you private secret and id are correct, ' \
                                                  'and that you have the correct pemirssions over your buckets.'
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class S3Connector(Connector):

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_id' not in self.auth_data:
                log['error']['client_id'] = 'auth_data must provide a client_id.'
                return {'log': log}
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide aws_access_key_id and aws_secret_access_key .'
                return {'log': log}

            self.connection_client = boto3.client('s3',
                                                  aws_access_key_id=self.auth_data['client_id'],
                                                  aws_secret_access_key=self.auth_data['client_secret'])
            return {'result': True}
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to AWS S3. Please check you private key, email and id are correct.'
            return {'log': log}

    @with_connection
    def __get_string_data(self, opts):
        """

        :param opts:
        :return:
        """
        bytes_buffer = io.BytesIO()
        self.connection_client.download_fileobj(Bucket = opts['bucket_name'], Key = opts['path'], Fileobj = bytes_buffer)
        byte_value = bytes_buffer.getvalue()
        str_value = byte_value.decode()  # python3, default decoding is utf-8
        return {'data': str_value}

    @with_connection
    def __fetch_object(self, opts):
        """Upload a file to diffgram from an S3 bucket

        :param s3_file_key: path of file to fetch from
        :return: file obj if file was uploaded, else False
        """
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        # This might be an issue. Currently not supporting urls with no expiration. Biggest time is 1 week.
        signed_url = self.connection_client.generate_presigned_url('get_object',
                                                                   Params={'Bucket': opts['bucket_name'],
                                                                           'Key': opts['path']},
                                                                   ExpiresIn=3600 * 24 * 6)  # 5 Days.

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
                    session=session,
                    member_id=opts['event_data']['request_user'],
                    kind='aws_s3_new_import_warning',
                    description=f"Skipped import for {opts['path']}, invalid file type.",
                    error_log=log,
                    project_id=project.id,
                    member=member,
                    success=False
                )
                return None

            # metadata = self.connection_client.head_object(Bucket=self.config_data['bucket_name'], Key=path)
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            created_input = packet.enqueue_packet(self.config_data['project_string_id'],
                                                  session=session,
                                                  media_url=signed_url,
                                                  media_type=media_type,
                                                  file_name = opts['path'],
                                                  job_id=opts.get('job_id'),
                                                  batch_id=opts.get('batch_id'),
                                                  video_split_duration=opts.get('video_split_duration'),
                                                  directory_id=opts.get('directory_id'),
                                                  extract_labels_from_batch=True,
                                                  member = member)
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session=session,
                member_id=opts['event_data']['request_user'],
                kind='aws_s3_new_import_success',
                description=f"New cloud import for {opts['path']}",
                error_log=opts,
                project_id=project.id,
                member=member,
                success=True
            )
        return created_input

    @with_connection
    def __fetch_folder(self, opts):
        paths = opts['path']
        if type(paths) != list:
            paths = [paths]
        for current_path in paths:
            kwargs = {'Bucket': opts['bucket_name'], 'Prefix': current_path}
            while True:
                resp = self.connection_client.list_objects_v2(**kwargs)
                for obj in resp['Contents']:
                    if not obj['Key'].endswith('/'):
                        opts_fetch_object = {}
                        opts_fetch_object.update(opts)
                        new_opts = {
                            'path': obj['Key'],
                            'directory_id': opts.get('directory_id'),
                            'batch_id': opts.get('batch_id'),
                            'bucket_name': opts.get('bucket_name'),
                        }
                        opts_fetch_object.update(new_opts)
                        self.__fetch_object(opts_fetch_object)
                try:
                    kwargs['ContinuationToken'] = resp['NextContinuationToken']
                except KeyError:
                    break

    @with_connection
    @with_s3_exception_handler
    def __start_folder_fetch(self, opts):

        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
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
    @with_s3_exception_handler
    def __list_s3_directories(self, opts):
        kwargs = {'Bucket': opts['bucket_name'], 'Prefix': opts['path'], 'Delimiter': '/'}
        resp = self.connection_client.list_objects_v2(**kwargs)
        keys = []
        for content in resp.get('CommonPrefixes', []):
            keys.append(content.get('Prefix'))
        return keys

    @with_connection
    @with_s3_exception_handler
    def __list_s3_files(self, opts):
        kwargs = {'Bucket': opts['bucket_name'], 'Prefix': opts['path'], 'Delimiter': '/'}
        resp = self.connection_client.list_objects_v2(**kwargs)
        keys = []
        for content in resp.get('Contents', []):
            if not content.get('Key').endswith('/'):
                keys.append(content.get('Key'))
        return keys

    @with_connection
    @with_s3_exception_handler
    def __get_folder_contents(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        prefix = opts['path']
        just_folders = opts.get('just_folders', False)
        files = []
        if not just_folders:
            files = sorted(self.__list_s3_files(opts))
        folders = sorted(list(self.__list_s3_directories(opts)))
        result = folders + files
        return {'result': result}

    @with_connection
    @with_s3_exception_handler
    def __list_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        keys = []
        kwargs = {'Bucket': opts['bucket_name'], 'Prefix': opts['path']}
        while True:
            resp = self.connection_client.list_objects_v2(**kwargs)
            for obj in resp.get('Contents', []):
                keys.append(obj['Key'])
            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break

        return {'result': keys}

    @with_connection
    @with_s3_exception_handler
    def __count_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input=opts,
                                                    spec_list=spec_list,
                                                    log=log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        count = 0
        kwargs = {'Bucket': opts['bucket_name'], 'Prefix': opts['path']}
        while True:
            resp = self.connection_client.list_objects_v2(**kwargs)
            all_objs = resp.get('Contents', [])
            only_files = list(filter(lambda x: not x.get('Key', '/').endswith('/'), all_objs))
            count += len(only_files)
            if count >= 10000:
                return {'result': '10,000+'}
            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break
        return {'result': count}

    @with_connection
    @with_s3_exception_handler
    def __list_buckets(self, opts):
        response = self.connection_client.list_buckets()
        result = []
        for bucket in response['Buckets']:
            result.append(bucket['Name'])
        return {'result': result}

    @with_connection
    @with_s3_exception_handler
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
            return log

        with sessionMaker.session_scope() as session:
            project = Project.get_by_string_id(session, self.config_data['project_string_id'])
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            export = session.query(Export).filter(Export.id == opts['export_id']).first()
            # Check perms and export status.
            export_check_result = check_export_permissions_and_status(export,
                                                                      self.config_data['project_string_id'],
                                                                      session)
            if regular_log.log_has_error(export_check_result):
                return export_check_result

            result = export_view_core(
                export=export,
                format=opts['format'],
                return_type='bytes')
            result = bytes(result, 'utf-8')
            filename = generate_file_name_from_export(export, session)
            if opts['path'] != '':
                key = f"{opts['path']}{filename}.{opts['format'].lower()}"
            else:
                key = f"{filename}.{opts['format'].lower()}"

            file = io.BytesIO(result)
            self.connection_client.upload_fileobj(file, opts['bucket_name'], key)
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session=session,
                member_id=opts['event_data']['request_user'],
                kind='aws_s3_new_export_success',
                description=f"New cloud export for {opts['path']}{filename}",
                error_log=opts,
                member=member,
                project_id=project.id,
                success=True
            )
            return {'result': True}

    def validate_s3_connection_read_write(self, bucket_name):
        test_file_path = 'diffgram_test_file.txt'
        log = regular_log.default()
        try:
            self.connection_client.put_object(Body = 'This is a diffgram test file',
                              Bucket = bucket_name,
                              Key = test_file_path,
                              ContentType = 'text/plain')

        except Exception as e:
            log['error']['s3_write_perms'] = 'Error Connecting to S3: Please check you have write permissions on the S3 bucket.'
            log['error']['details'] = traceback.format_exc()
            return False, log
        try:
            signed_url = self.connection_client.generate_presigned_url('get_object',
                                                       Params = {'Bucket': bucket_name, 'Key': test_file_path},
                                                       ExpiresIn = 3600 * 24 * 6)
            resp = requests.get(signed_url, verify=False if self.auth_data['disabled_ssl_verify'] else None)
            if resp.status_code != 200:
                raise Exception(
                    f"Error when accessing presigned URL: Status({resp.status_code}). Error: {resp.text}")
        except:
            log['error']['s3_write_perms'] = 'Error Connecting to S3: Please check you have read permissions on the S3 bucket.'
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

        if bucket_names and len(bucket_names) > 0:
            validation_result, log = self.validate_s3_connection_read_write(bucket_names[0])
            if len(log['error'].keys()) > 0:
                return {'log': log}


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
        if action_type == 'get_string_data':
            return self.__get_string_data(opts)
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
