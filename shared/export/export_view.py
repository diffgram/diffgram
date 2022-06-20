import json
from shared.data_tools_core import Data_tools
from shared.database.export import Export
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()
data_tools = Data_tools().data_tools


def export_view_core(export: Export, format: str = "JSON", return_type: str = "url") -> str:
    """
        Returns export data, for usage on API handlers
        or queue consumers. No permissions are cheked here, make sure to use
        in conjunction with the appropriate permissions handlers.
    :param export:
    :param format:
    :param return_type:
    :return:
    """

    # TODO format string validation?

    blob_name = None
    if export.kind == "Annotations":

        if format == "JSON":
            blob_name = export.json_blob_name

        if format == "YAML":
            blob_name = export.yaml_blob_name

    if export.kind == "TF Records":
        blob_name = export.tf_records_blob_name

    if blob_name is None:
        logger.error(f'Invalid export kind or format: Kind: {export.kind}, format: {format}')
        return
    expiration_offset = 60 * 5  # seconds

    # TODO not clear what we want this flag to be...
    # I think it should be seperate from format maybe?
    # ie a new attribute like "return_kind" or something?
    if return_type in ['data', 'bytes']:
        # Caution this is in Bytes
        blob_data = data_tools.get_string_from_blob(blob_name)

        if return_type == 'bytes':
            return blob_data

        # We don't seem to need decode with json.loads()
        # blob_data = blob_data.decode()

        json_data = json.loads(blob_data)

        return json_data

    # Default case URL
    url = data_tools.build_secure_url(
        blob_name,
        expiration_offset,
        bucket = "ml")
    return url
