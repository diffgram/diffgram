import time
import traceback
import requests
import shutil
from shared.data_tools_core import data_tools
from shared.data_tools_core import DiffgramBlobObjectType
from sqlalchemy.orm.session import Session
from shared.database.image import Image
from shared.database.source_control.file import File
from shared.database.text_file import TextFile
from shared.regular import regular_log
from shared.shared_logger import get_shared_logger
from shared.database.connection.connection import Connection
from shared.connection.connection_strategy import ConnectionStrategy, CONNECTIONS_MAPPING
from shared.connection.s3_connector import S3Connector
from shared.regular.regular_member import get_member
from shared.database.auth.member import Member
import tempfile

logger = get_shared_logger()

ALLOWED_CONNECTION_SIGNED_URL_PROVIDERS = ['amazon_aws', 'microsoft_azure']


def get_blob_file_extension(blob_path: str) -> str:
    splitted = blob_path.split('.')
    if len(splitted) == 1:
        return None
    return splitted[len(splitted) - 1]


def get_blob_file_name(blob_path: str) -> str:
    splitted = blob_path.split('/')
    return splitted[len(splitted) - 1]


def get_blob_file_path_without_name(blob_path: str) -> str:
    file_name = get_blob_file_name(blob_path)
    return blob_path.split(file_name)[0]


def default_url_regenerate(session: Session,
                           blob_object: DiffgramBlobObjectType,
                           new_offset_in_seconds: int) -> [DiffgramBlobObjectType, dict]:
    """
        Regenerates signed URL using blob default storage provider from DataTools().
    :param session:
    :param blob_object:
    :param new_offset_in_seconds:
    :return:
    """
    log = regular_log.default()
    try:
        blob_object.url_signed = data_tools.build_secure_url(blob_object.url_signed_blob_path, new_offset_in_seconds)
        blob_object.url_signed_expiry = time.time() + new_offset_in_seconds
        if type(blob_object) == Image and blob_object.url_signed_thumb_blob_path:
            blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path,
                                                                       new_offset_in_seconds)
        session.add(blob_object)

        # Extra assets (Depending on type)
        if type(blob_object) == Image and blob_object.url_signed_thumb_blob_path:
            blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path,
                                                                       new_offset_in_seconds)
        if type(blob_object) == TextFile and blob_object.tokens_url_signed_blob_path:
            blob_object.tokens_url_signed = data_tools.build_secure_url(blob_object.tokens_url_signed_blob_path,
                                                                        new_offset_in_seconds)

    except Exception as e:
        msg = traceback.format_exc()
        logger.error(msg)
        if type(blob_object) == Image:
            blob_object.error = msg
        log['error']['default_url_regenerate'] = msg
        return blob_object, log
    return blob_object, log




def get_from_connector(connector, params, log):
    connector.connect()
    response = connector.fetch_data(params)
    return response, log


def upload_thumbnail_for_connection_image(session: Session,
                                          blob_object: DiffgramBlobObjectType,
                                          connection_id: int,
                                          bucket_name: str,
                                          new_offset_in_seconds: int,
                                          member: Member,
                                          access_token: str = None,
                                          reference_file: File = None) -> [DiffgramBlobObjectType, dict]:
    log = regular_log.default()
    extension = get_blob_file_extension(blob_path = blob_object.url_signed_blob_path)
    file_dir = get_blob_file_path_without_name(blob_path = blob_object.url_signed_blob_path)
    file_name = get_blob_file_name(blob_path = blob_object.url_signed_blob_path)
    blob_path_dirs = get_blob_file_path_without_name(blob_path = blob_object.url_signed_blob_path)
    blob_path_thumb = f'{blob_path_dirs}thumb/{file_name}'
    connection = Connection.get_by_id(session = session, id = connection_id)
    params = {
        'bucket_name': bucket_name,
        'path': blob_path_thumb,
        'expiration_offset': new_offset_in_seconds,
        'access_token': access_token,
        'action_type': 'custom_image_upload_url',
        'event_data': {
            'request_user': member.user_id
        }
    }
    client, log = get_custom_url_supported_connector(
        session = session,
        log = log,
        connection_id = connection_id,
    )
    if regular_log.log_has_error(log):
        return blob_object, log
    put_data, log = get_from_connector(connector = client, params = params, log = log)
    if regular_log.log_has_error(log):
        if 'blob_exists' in log['error']:
            log = regular_log.default()
            blob_object.url_signed_thumb_blob_path = blob_path_thumb
            session.add(blob_object)
        return blob_object, log
    if put_data is None:
        return blob_object, log
    url = put_data.get('url')
    fields = put_data.get('fields')
    headers = put_data.get('headers')
    if not url:
        return blob_object, log
    # Download Asset and re upload to url
    temp_dir = tempfile.mkdtemp()
    temp_dir_path_and_filename = f"{temp_dir}/{file_name}.{extension}"
    # Get image

    response = requests.get(blob_object.url_signed)
    if not response.ok:
        msg = f'Failed to upload thumb. Error getting blob url {blob_object.url_signed_blob_path}'
        logger.error(msg)
        log['error']['upload_thumb'] = msg
        return blob_object, log
    img_data = response.content
    with open(temp_dir_path_and_filename, 'wb') as file_handler:
        file_handler.write(img_data)

    # Now upload file to blob storage
    with open(temp_dir_path_and_filename, 'rb') as file_handler:
        if connection.integration_name == 'amazon_aws':
            upload_resp = requests.put(url, data = file_handler.read(), timeout = 30)
        elif connection.integration_name == 'microsoft_azure':
            upload_resp = requests.put(url, data = file_handler, headers=headers)
        if not upload_resp.ok:
            msg = f'Failed to upload thumb. Error posting [{upload_resp.status_code}] {upload_resp.text}'
            logger.error(msg)
            log['error']['upload_thumb'] = msg
            return blob_object, log
        blob_object.url_signed_thumb_blob_path = blob_path_thumb
        session.add(blob_object)
    shutil.rmtree(temp_dir)  # delete directory
    return blob_object, log


def get_custom_url_supported_connector(session: Session, log: dict, connection_id: int) -> [object, dict]:
    """
        Gets the connector object and checks if it supports custom signed urls with a custom service.
    :param session:
    :param log:
    :param connection_id:
    :param connection:
    :return:
    """
    connection = Connection.get_by_id(session = session, id = connection_id)
    if connection is None:
        msg = f'connection id: {connection_id} not found.'
        log['error']['connection_id'] = msg
        logger.error(msg)
        return None, log
    if connection.integration_name not in ALLOWED_CONNECTION_SIGNED_URL_PROVIDERS:
        msg = f'Unsupported connection provider for URL regeneration {connection.id}:{connection.integration_name}'
        log['error']['unsupported'] = msg
        log['error']['supported_providers'] = ALLOWED_CONNECTION_SIGNED_URL_PROVIDERS
        logger.error(msg)
        return None, log

    connection_strategy = ConnectionStrategy(
        connection_id = connection_id,
        session = session)

    client, success = connection_strategy.get_connector(connection_id = connection_id)
    if not success:
        msg = f'Failed to get connector for connection {connection_id}'
        log['error']['connector'] = msg
        logger.error(msg)
        return None, log

    return client, log



def generate_text_token_url(
    session: Session,
    blob_object: DiffgramBlobObjectType,
    params: dict,
    log: dict,
    client: any,
):
    params['path'] = blob_object.tokens_url_signed_blob_path
    token_signed_url, log = get_from_connector(connector = client, params = params, log = log)
    if regular_log.log_has_error(log):
        return blob_object, log
    blob_object.tokens_url_signed = token_signed_url
    session.add(blob_object)


def connection_url_regenerate(session: Session,
                              blob_object: DiffgramBlobObjectType,
                              connection_id: int,
                              bucket_name: str,
                              new_offset_in_seconds: int,
                              access_token: str = None,
                              reference_file: File = None) -> list[DiffgramBlobObjectType, dict]:

    log = regular_log.default()
    member = get_member(session = session)

    params = {
        'bucket_name': bucket_name,
        'path': blob_object.url_signed_blob_path if reference_file is None else reference_file.get_blob_path(),
        'expiration_offset': new_offset_in_seconds,
        'access_token': access_token,
        'action_type': 'get_pre_signed_url',
        'event_data': {
            'request_user': member.user_id
        }
    }
    client, log = get_custom_url_supported_connector(
        session = session,
        log = log,
        connection_id = connection_id,
    )
    if regular_log.log_has_error(log):
        return blob_object, log

    result, log = get_from_connector(
        connector = client, 
        params = params, 
        log = log)
    
    if regular_log.log_has_error(log):
        return blob_object, log
    
    blob_object.url_signed = result.get('signed_url')
    blob_object.url_signed_thumb = result.get('signed_url')
    error = result.get('error')
    if error:
        try:
            blob_object.error = result.get('error')
        except:
            blob_object.error = str(result.get('error'))
    # Extra assets (Depending on type)

    if type(blob_object) == TextFile and blob_object.tokens_url_signed_blob_path:
        blob_object, log = generate_text_token_url(
            session = session,
            blob_object = blob_object,
            params = params,
            log = log,
            client = client,
        )
    session.add(blob_object)    # TODO review if needed to add to session here
    # If it's unique for every user then it's not clear why we would need to do this
    # And adds processing delays for viewing large amounts at once.
    return blob_object, log


def blob_regenerate_url(blob_object: DiffgramBlobObjectType,
                        session: Session,
                        connection_id: int = None,
                        bucket_name: str = None,
                        access_token: str = None,
                        reference_file: File = None) -> list[object, dict]:

    if not blob_object.url_signed_blob_path:
        return

    strategy = determine_url_regenerate_strategy(
        connection_id = connection_id,
        bucket_name = bucket_name)

    should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(blob_object, session)
    if should_regenerate is not True and strategy != 'connection':
        return

    logger.debug(f"Regenerating with {strategy} strategy")

    if strategy == "default":
        blob_object, log = default_url_regenerate(
            session = session,
            blob_object = blob_object,
            new_offset_in_seconds = new_offset_in_seconds
        )

    if strategy == "connection":
        logger.debug(f'Generate Signed Url with connection {connection_id} on bucket {bucket_name}')
        blob_object, log = connection_url_regenerate(
            session = session,
            blob_object = blob_object,
            connection_id = connection_id,
            bucket_name = bucket_name,
            new_offset_in_seconds = new_offset_in_seconds,
            reference_file = reference_file,
            access_token = access_token
        )

    if regular_log.log_has_error(log):
        logger.error(f'Failed to regenerate Blob URL {log}')
        blob_object.url_signed = None
        blob_object.error = str(log)
        session.add(blob_object)
        return blob_object, log

    return blob_object, log


def determine_url_regenerate_strategy(connection_id,
                                      bucket_name) -> str:
    default_strategy = "default"
    strategy = default_strategy

    if connection_id is not None and bucket_name is not None:
        strategy = "connection"

    return strategy
