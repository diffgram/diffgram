import time
from shared.data_tools_core import data_tools
from shared.data_tools_core import DiffgramBlobObjectType
from sqlalchemy.orm.session import Session
from shared.database.image import Image


def default_url_regenerate(session: Session,
                           blob_object: DiffgramBlobObjectType,
                           new_offset_in_seconds: int) -> DiffgramBlobObjectType:
    blob_object.url_signed = data_tools.build_secure_url(blob_object.url_signed_blob_path, new_offset_in_seconds)
    blob_object.url_signed_expiry = time.time() + new_offset_in_seconds
    if type(blob_object) == Image:
        blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path, new_offset_in_seconds)
    session.add(blob_object)
    return blob_object


def connection_url_regenerate():
    pass


def blob_regenerate_url(blob_object: DiffgramBlobObjectType,
                        session: Session,
                        connection_id = None,
                        bucket_name = None):
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
    if should_regenerate is True:
        if connection_id is None and bucket_name is None:
            default_url_regenerate(
                session = session,
                blob_object = blob_object,
                new_offset_in_seconds = new_offset_in_seconds
            )
        else:
            connection_url_regenerate()
