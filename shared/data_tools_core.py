import time
from shared.settings import settings
from shared.data_tools_core_gcp import DataToolsGCP
from shared.data_tools_core_s3 import DataToolsS3
from shared.data_tools_core_minio import DataToolsMinio
from shared.data_tools_core_azure import DataToolsAzure
from shared.utils.singleton import Singleton
from shared.database.image import Image
from shared.database.audio.audio_file import AudioFile
from shared.database.geospatial.geo_asset import GeoAsset
from shared.database.point_cloud.point_cloud import PointCloud
from sqlalchemy.orm.session import Session

# Videos Excluded for now
DiffgramBlobObjectType = Image or AudioFile or GeoAsset or PointCloud


class Data_tools(metaclass = Singleton):
    """
        Factory Class For Data_tools Class implementation.
        Depending on the setting set in settings.DIFFGRAM_STATIC_STORAGE_PROVIDER
        this class will instantiatiate a different cloud provider implementation for data tools
        which will manager the upload, download of blobs from the cloud storage provider.
    """

    def __init__(self):
        provider = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER

        if not provider:
            raise ValueError("No DIFFGRAM_STATIC_STORAGE_PROVIDER env var set. valid values are [gcp, aws, azure]")

        if provider == 'gcp':
            self.data_tools = DataToolsGCP()
        elif provider == 'aws':
            self.data_tools = DataToolsS3()
        elif provider == 'minio':
            self.data_tools = DataToolsMinio()
        elif provider == 'azure':
            self.data_tools = DataToolsAzure()

    def determine_if_should_regenerate_url(self,
                                           blob_object: DiffgramBlobObjectType,
                                           session: Session,
                                           url_signed_expiry: int = None):
        if not session: return False, None
        minimum_secs_valid = settings.SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID
        new_offset_in_seconds = settings.SIGNED_URL_CACHE_NEW_OFFSET_SECONDS_VALID

        time_to_check = time.time() + minimum_secs_valid

        if url_signed_expiry is None:
            url_signed_expiry = blob_object.url_signed_expiry

        if url_signed_expiry is None:
            return True, new_offset_in_seconds

        url_signed_expiry = int(float(blob_object.url_signed_expiry))

        if url_signed_expiry <= settings.URL_SIGNED_REFRESH + (new_offset_in_seconds):
            return True, new_offset_in_seconds

        if url_signed_expiry <= time_to_check:
            return True, new_offset_in_seconds

        return False, None


data_tools_instance = Data_tools()
data_tools = data_tools_instance.data_tools
data_tools.determine_if_should_regenerate_url = data_tools_instance.determine_if_should_regenerate_url
