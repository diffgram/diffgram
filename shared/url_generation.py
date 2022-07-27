import time
import traceback

from shared.data_tools_core import data_tools
from shared.data_tools_core import DiffgramBlobObjectType
from sqlalchemy.orm.session import Session
from shared.database.image import Image
from shared.database.source_control.file import File
from shared.database.text_file import TextFile
from shared.regular import regular_log
from shared.shared_logger import get_shared_logger
from shared.database.connection.connection import Connection
from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.s3_connector import S3Connector
from shared.regular.regular_member import get_member
logger = get_shared_logger()

ALLOWED_CONNECTION_SIGNED_URL_PROVIDERS = ['amazon_aws']


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
        if type(blob_object) == Image:
            blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path,
                                                                       new_offset_in_seconds)
        session.add(blob_object)

        # Extra assets (Depending on type)
        if type(blob_object) == Image and blob_object.url_signed_thumb_blob_path:
            blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path, new_offset_in_seconds)
            blob_object.url_ = time.time() + new_offset_in_seconds
        if type(blob_object) == TextFile and blob_object.tokens_url_signed_blob_path:
            blob_object.tokens_url_signed = data_tools.build_secure_url(blob_object.tokens_url_signed_blob_path, new_offset_in_seconds)

    except Exception as e:
        msg = traceback.format_exc()
        logger.error(msg)
        log['error']['default_url_regenerate'] = msg
        return blob_object, log
    return blob_object, log


def get_url_from_connector(connector, params, log):
    """
        Gets signed URL from given connector.
    :param connector:
    :param params:
    :param log:
    :return:
    """
    connector.connect()
    response = connector.fetch_data(params)
    if response is None or response.get('result') is None:
        msg = f'Error regenerating URL: {params}. Response: {response}'
        log['error']['connector_client'] = msg
        logger.error(msg)
        return None, log
    signed_url = response.get('result')
    return signed_url, log


def connection_url_regenerate(session: Session,
                              blob_object: DiffgramBlobObjectType,
                              connection_id: int,
                              bucket_name: int,
                              new_offset_in_seconds: int,
                              reference_file: File = None) -> [DiffgramBlobObjectType, dict]:
    """
        Regenerates signed url from the given connection ID, bucket and blob path.
    :param session:
    :param blob_object:
    :param connection_id:
    :param bucket_name:
    :param new_offset_in_seconds:
    :return:
    """

    log = regular_log.default()
    connection = Connection.get_by_id(session = session, id = connection_id)
    if connection is None:
        msg = f'connection id: {connection_id} not found.'
        log['error']['connection_id'] = msg
        logger.error(msg)
        return blob_object, log
    member = get_member(session = session)
    params = {
        'bucket_name': bucket_name,
        'path': blob_object.url_signed_blob_path if reference_file is None else reference_file.get_blob_path(),
        'expiration_offset': new_offset_in_seconds,
        'action_type': 'get_pre_signed_url',
        'event_data': {
            'request_user': member.user_id
        }
    }

    if connection.integration_name not in ALLOWED_CONNECTION_SIGNED_URL_PROVIDERS:
        msg = f'Unsupported connection provider for URL regeneration {connection.id}:{connection.integration_name}'
        log['error']['unsupported'] = msg
        logger.error(msg)
        return blob_object, log

    connection_strategy = ConnectionStrategy(
        connector_id = connection_id,
        session = session)

    client, success = connection_strategy.get_connector(connector_id = connection_id)
    if not success:
        msg = f'Failed to get connector for connection {connection_id}'
        log['error']['connector'] = msg
        logger.error(msg)
        return blob_object, log
    signed_url, log = get_url_from_connector(connector = client, params = params, log = log)
    if regular_log.log_has_error(log):
        return blob_object, log
    if regular_log.log_has_error(log):
        return blob_object, log
    blob_object.url_signed = signed_url

    # Extra assets (Depending on type)
    if type(blob_object) == Image and blob_object.url_signed_thumb_blob_path:
        params['path'] = blob_object.url_signed_thumb_blob_path
        thumb_signed_url, log = get_url_from_connector(connector = client, params = params, log = log)
        if regular_log.log_has_error(log):
            return blob_object, log
        blob_object.url_signed_thumb = thumb_signed_url

    # Extra assets (Depending on type)
    if type(blob_object) == TextFile and blob_object.tokens_url_signed_blob_path:
        params['path'] = blob_object.tokens_url_signed_blob_path
        thumb_signed_url, log = get_url_from_connector(connector = client, params = params, log = log)
        if regular_log.log_has_error(log):
            return blob_object, log
        blob_object.url_signed_thumb = thumb_signed_url

    return blob_object, log


def blob_regenerate_url(blob_object: DiffgramBlobObjectType,
                        session: Session,
                        connection_id = None,
                        bucket_name = None,
                        reference_file: File = None):
    """
        Regenerates the signed url of the given blob object.
    :param blob_object:
    :param session:
    :param connection_id:
    :param bucket_name:
    :return:
    """
    if not blob_object.url_signed_blob_path:
        return

    should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(blob_object, session)

    if should_regenerate is not True: 
        return

    strategy = determine_url_regenerate_strategy(
        connection_id = connection_id,
        bucket_name = bucket_name)

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
            reference_file = reference_file
        )

    if regular_log.log_has_error(log):
        logger.error(f'Failed to regenerate Blob URL {log}')
        blob_object.url_signed_blob_path = None
        return blob_object, log
    return blob_object, log


def determine_url_regenerate_strategy(connection_id,
                                      bucket_name) -> str:

    default_strategy = "default"
    strategy = default_strategy

    if connection_id is not None and bucket_name is not None:
        strategy = "connection"

    return strategy 
