import time
from shared.database.common import data_tools
from data_tools_core import DiffgramBlobObjectType
from sqlalchemy.orm.session import Session


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

    if not blob_object.url_signed_blob_path and (connection_id is None or bucket_name is None):
        return
    should_regenerate, new_offset_in_seconds = data_tools.determine_if_should_regenerate_url(blob_object, session)
    if should_regenerate is True:
        blob_object.url_signed = data_tools.build_secure_url(blob_object.url_signed_blob_path, new_offset_in_seconds)
        blob_object.url_signed_thumb = data_tools.build_secure_url(blob_object.url_signed_thumb_blob_path,
                                                                   new_offset_in_seconds)
        blob_object.url_signed_expiry = time.time() + new_offset_in_seconds
        session.add(blob_object)
