# OPEN CORE - ADD
from shared.settings import settings
from shared.data_tools_core_gcp import DataToolsGCP
from shared.data_tools_core_s3 import DataToolsS3
from shared.data_tools_core_azure import DataToolsAzure
from shared.utils.singleton import Singleton


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


data_tools = Data_tools().data_tools
