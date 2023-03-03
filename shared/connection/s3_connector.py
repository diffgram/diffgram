# OPENCORE - ADD
import boto3
import traceback
import threading
import io
import requests
import urllib.parse

import mimetypes
from shared.regular.regular_api import *
from shared.auth.OAuth2Provider import OAuth2Provider
from shared.helpers import sessionMaker
from shared.database.project import Project
from shared.database.auth.member import Member
from shared.connection.connectors.connectors_base import Connector, with_connection
from shared.ingest import packet
from pathlib import Path
from shared.export.export_view import export_view_core
from shared.database.export import Export
from shared.export.export_utils import generate_file_name_from_export, check_export_permissions_and_status
from shared.regular import regular_log

from shared.data_tools_core_s3 import DataToolsS3
from botocore.config import Config
from shared.ingest.allowed_ingest_extensions import images_allowed_file_names, videos_allowed_file_names


def with_s3_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            return f(*args)
        except Exception as e:
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class S3Connector(Connector):
    url_signer_service: str or None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "amazon_aws"

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_id' not in self.auth_data:
                log['error']['client_id'] = 'auth_data must provide a client_id.'
                return {'log': log}
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide aws_access_key_id and aws_secret_access_key .'
                return {'log': log}

            config = None
            if self.auth_data.get('aws_v4_signature'):
                config = Config(signature_version = 's3v4')

            self.connection_client = DataToolsS3.get_client(
                aws_access_key_id = self.auth_data['client_id'],
                aws_secret_access_key = self.auth_data['client_secret'],
                config = config,
                region_name = self.auth_data.get('aws_region')
            )
            self.url_signer_service = None
            if self.auth_data.get('url_signer_service') is not None and self.auth_data.get('url_signer_service') != '':
                self.url_signer_service = self.auth_data.get('url_signer_service')
                if self.url_signer_service.endswith('/'):
                    # Remove trailing slash
                    self.url_signer_service = self.url_signer_service.rstrip(self.url_signer_service[-1])

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
        self.connection_client.download_fileobj(Bucket = opts['bucket_name'], Key = opts['path'],
                                                Fileobj = bytes_buffer)
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
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}
        # This might be an issue. Currently not supporting urls with no expiration. Biggest time is 1 week.
        signed_url = self.connection_client.generate_presigned_url('get_object',
                                                                   Params = {'Bucket': opts['bucket_name'],
                                                                             'Key': opts['path']},
                                                                   ExpiresIn = 3600 * 24 * 6)  # 5 Days.

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
                    description = f"Skipped import for {opts['path']}, invalid file type.",
                    error_log = log,
                    project_id = project.id,
                    member = member,
                    success = False
                )
                return None

            # metadata = self.connection_client.head_object(Bucket=self.config_data['bucket_name'], Key=path)
            member = session.query(Member).filter(Member.user_id == opts['event_data']['request_user']).first()
            created_input = packet.enqueue_packet(self.config_data['project_string_id'],
                                                  session = session,
                                                  media_url = signed_url,
                                                  media_type = media_type,
                                                  file_name = opts['path'],
                                                  job_id = opts.get('job_id'),
                                                  batch_id = opts.get('batch_id'),
                                                  video_split_duration = opts.get('video_split_duration'),
                                                  directory_id = opts.get('directory_id'),
                                                  extract_labels_from_batch = True,
                                                  member = member)
            log = regular_log.default()
            log['opts'] = opts
            Event.new(
                session = session,
                member_id = opts['event_data']['request_user'],
                kind = 'aws_s3_new_import_success',
                description = f"New cloud import for {opts['path']}",
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
        for current_path in paths:
            kwargs = {'Bucket': opts['bucket_name'], 'Prefix': current_path}
            while True:
                resp = self.connection_client.list_objects_v2(**kwargs)
                if resp.get('Contents'):
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

    def __custom_presign_url(self, bucket_name: str, blob_name: str, access_token_param: str = None) -> str or None:
        from shared.helpers.permissions import get_session_string
        if access_token_param is None:
            access_token = get_session_string()
        else:
            access_token = access_token_param
        content_type = mimetypes.guess_type(blob_name)

        if content_type is None:
            content_type = "image/png"
        elif len(content_type) > 1:
            content_type = content_type[0]
        headers = {
            'Authorization': f'{access_token}',
            'Content-Type': content_type
        }

        logger.info(f'Custom Signer Headers: {headers}')
        blob_name_encoded = urllib.parse.quote(blob_name, safe = '')
        url_path = f'{self.url_signer_service}/{bucket_name}'

        try:
            params = {'key': blob_name, "method": "get"}
            result = requests.get(url = url_path, headers = headers, params = params)
            if result.status_code == 200:

                data = result.json()
                url_result = data['url']
                logger.debug(f'GET Presign URL response {result.text}')
                return url_result
            else:
                logger.error(f'Error generating signed url with: {url_path}')
                logger.error(f'Error payload: {result.text}')
                logger.error(f'Request payload: {params}')
                return None
        except Exception as e:
            err = traceback.format_exc()
            logger.error(f'Error generating signed url with: {url_path}')
            logger.error(f'Error payload: {err}')
            return None

    def __image_upload_url(self, bucket_name: str, blob_name: str, expiration_offset: int, log: dict) -> dict:
        """
            Generates presigned PUT for uploading data using boto3
        :param bucket_name:
        :param blob_name:
        :param log:
        :return:
        """
        filename = blob_name.split("/")[-1]
        signed_url_data = self.connection_client.generate_presigned_post(Bucket=bucket_name,
                                                                    Key=blob_name,
                                                                    ExpiresIn=expiration_offset)
        return {'result': signed_url_data}

    def __custom_image_upload_url(self, opts: dict) -> dict or None:
        """
            Generates a Put signed url for uploading data using custom signer.
            If no self.url_signer_service it defaults to the boto3 signer using
            the connection credentials.
        :param opts:
        :return:
        """
        spec_list = [{'bucket_name': str, 'path': str, 'expiration_offset': int}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if regular_log.log_has_error(log):
            return {'log': log}
        bucket_name = opts.get('bucket_name')
        expiration_offset = opts.get('expiration_offset')
        blob_name = opts.get('path')
        if self.url_signer_service is None:
            return self.__image_upload_url(
                bucket_name = bucket_name,
                log = log,
                expiration_offset = expiration_offset,
                blob_name = blob_name
            )
        if self.url_signer_service:
            access_token_param = opts.get('access_token')
            from shared.helpers.permissions import get_session_string
            if access_token_param is None:
                access_token = get_session_string()
            else:
                access_token = access_token_param
            content_type = mimetypes.guess_type(blob_name)

            if content_type is None:
                content_type = "image/png"
            elif len(content_type) > 1:
                content_type = content_type[0]
            headers = {
                'Authorization': f'{access_token}',
                'Content-Type': content_type
            }
            blob_name_encoded = urllib.parse.quote(blob_name, safe = '')
            url_path = f'{self.url_signer_service}/{bucket_name}'
            try:
                params = {'key': blob_name, "method": "put"}
                result = requests.get(url = url_path, headers = headers, params = params)
                if result.status_code == 200:
                    data = result.json()
                    logger.info(f'Signer Upload URL JSON {data}')
                    return {'result': data}
                elif result.status_code == 409:
                    log['error']['blob_exists'] = 'Thumbnail blob already exists'
                    logger.error(f'Error Thumbnail blob already exists: [{result.status_code}] {result.text}')
                    return {'log': log}
                else:
                    logger.error(f'Error generating signed url with: [{result.status_code}] {url_path}')
                    logger.error(f'Error payload: {result.text}')
                    return None
            except Exception as e:
                err = traceback.format_exc()
                logger.error(f'Error generating signed url with: {url_path}')
                logger.error(f'Error payload: {err}')
                return None

    @with_connection
    def __get_pre_signed_url(self, opts):
        spec_list = [{'bucket_name': str, 'path': str, 'expiration_offset': int}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if regular_log.log_has_error(log):
            return {'log': log}
        blob_name = opts['path']
        expiration_offset = opts['expiration_offset']
        if blob_name is None:
            log['error']['blob_path'] = 'blob path cannot be None'
            return {'log': log}
        filename = blob_name.split("/")[-1]
        bucket_name = opts['bucket_name']

        if self.url_signer_service:
            signed_url = self.__custom_presign_url(bucket_name = bucket_name,
                                                   blob_name = blob_name)
            return {'result': signed_url}

        signed_url = self.connection_client.generate_presigned_url('get_object',
                                                                   Params = {
                                                                       'Bucket': bucket_name,
                                                                       'Key': blob_name},
                                                                   ExpiresIn = int(expiration_offset))
        return {'result': signed_url}

    @with_connection
    @with_s3_exception_handler
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
            files = sorted(self.__list_s3_files(opts))
        folders = sorted(list(self.__list_s3_directories(opts)))
        result = folders + files
        return {'result': result}

    @with_connection
    @with_s3_exception_handler
    def __list_objects(self, opts):
        spec_list = [{'bucket_name': str, 'path': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
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
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
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
            if regular_log.log_has_error(export_check_result):
                return export_check_result

            result = export_view_core(
                export = export,
                format = opts['format'],
                return_type = 'bytes')
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
                session = session,
                member_id = opts['event_data']['request_user'],
                kind = 'aws_s3_new_export_success',
                description = f"New cloud export for {opts['path']}{filename}",
                error_log = opts,
                member = member,
                project_id = project.id,
                success = True
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
            log['error'][
                's3_write_perms'] = 'Error Connecting to S3: Please check you have write permissions on the S3 bucket.'
            log['error']['details'] = traceback.format_exc()
            return False, log
        try:
            signed_url = self.connection_client.generate_presigned_url('get_object',
                                                                       Params = {'Bucket': bucket_name,
                                                                                 'Key': test_file_path},
                                                                       ExpiresIn = 3600 * 24 * 6)
            resp = requests.get(signed_url, verify = not self.auth_data['disabled_ssl_verify'])
            if resp.status_code != 200:
                raise Exception(
                    f"Error when accessing presigned URL: Status({resp.status_code}). Error: {resp.text}")
        except:
            log['error'][
                's3_write_perms'] = 'Error Connecting to S3: Please check you have read permissions on the S3 bucket.'
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
        if action_type == 'get_pre_signed_url':
            return self.__get_pre_signed_url(opts)
        if action_type == 'custom_image_upload_url':
            return self.__custom_image_upload_url(opts)

    @with_connection
    def put_data(self, opts):
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'send_export':
            return self.__send_export(opts)
