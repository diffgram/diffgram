# OPEN CORE - ADD
from shared.settings import settings
from shared.data_tools_core_gcp import DataToolsGCP
from shared.data_tools_core_s3 import DataToolsS3
from shared.data_tools_core_azure import DataToolsAzure
from shared.utils.singleton import Singleton
import time


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
        elif provider == 'azure':
            self.data_tools = DataToolsAzure()


    def determine_if_should_regenerate_url(self, object, session, url_signed_expiry=None):
        if not session: return False, None
        minimum_days_valid = 30 * 12  # this should always be lower then new offset
        new_offset_days_valid = 30 * 14
        one_day = 86400
        time_to_check = time.time() + (one_day * minimum_days_valid)
        new_offset_in_seconds = one_day * new_offset_days_valid

        if url_signed_expiry is None:
            url_signed_expiry = object.url_signed_expiry

        if url_signed_expiry is None:
            return True, new_offset_in_seconds

        if url_signed_expiry <= settings.URL_SIGNED_REFRESH + (one_day * minimum_days_valid):
            return True, new_offset_in_seconds

        if url_signed_expiry <= time_to_check:
            return True, new_offset_in_seconds

        return False, None


data_tools_instance = Data_tools()
data_tools = data_tools_instance.data_tools
data_tools.determine_if_should_regenerate_url = data_tools_instance.determine_if_should_regenerate_url