import boto3
from shared.settings import settings

from .data_tools_core_s3 import Config
from .data_tools_core_s3 import DataToolsS3
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()

class DataToolsMinio(DataToolsS3):
    """
        Data tools Implementation for Minio S3.

        Requires setting the following settings
        - DIFFGRAM_MINIO_ENDPOINT_URL
        - DIFFGRAM_MINIO_ACCESS_KEY_ID
        - DIFFGRAM_MINIO_ACCESS_KEY_SECRET
        - DIFFGRAM_MINIO_DISABLED_SSL_VERIFY
        - DIFFGRAM_S3_BUCKET_REGION
        - DIFFGRAM_S3_BUCKET_NAME

    """
    def build_secure_url(self, blob_name: str, expiration_offset: int = None, bucket: str = "web"):
        """
            Builds a presigned URL to access the given blob path.
        :param blob_name: The path to the blob for the presigned URL
        :param expiration_offset: The expiration time for the presigned URL
        :param bucket: string for the bucket type (either 'web' or 'ml') defaults to 'web'
        :return: the string for the presigned url
        """
        signed_url = super().build_secure_url(blob_name = blob_name,
                                              expiration_offset = expiration_offset,
                                              bucket = bucket)
        if settings.DOCKER_COMPOSE_CONTEXT == True:
            # note need to proxy request through local dispatcher so users can access from the browser
            return self.get_local_dispatcher_proxy_path(signed_url)
        else:
            return signed_url

    def get_local_dispatcher_proxy_path(self, signed_url):
        return signed_url.replace(settings.DIFFGRAM_MINIO_ENDPOINT_URL, 'http://localhost:8085/proxy_to_minio')

    def __init__(self):

        self.s3_bucket_name = settings.DIFFGRAM_S3_BUCKET_NAME
        self.s3_bucket_name_ml = settings.ML__DIFFGRAM_S3_BUCKET_NAME

        config = None
        if settings.IS_DIFFGRAM_S3_V4_SIGNATURE:
            config=Config(signature_version='s3v4')

        self.s3_client = DataToolsMinio.get_client(
            endpoint_url = settings.DIFFGRAM_MINIO_ENDPOINT_URL,
            access_key_id = settings.DIFFGRAM_MINIO_ACCESS_KEY_ID,
            secret_access_key = settings.DIFFGRAM_MINIO_ACCESS_KEY_SECRET,
            region_name = settings.DIFFGRAM_S3_BUCKET_REGION,
            verify = not settings.DIFFGRAM_MINIO_DISABLED_SSL_VERIFY,
            config = config)


    @staticmethod
    def get_client(endpoint_url,
                   access_key_id, 
                   secret_access_key,
                   region_name = None, 
                   verify = False,
                   config = None):

        return boto3.client(
            's3',
            endpoint_url = endpoint_url,
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            region_name = region_name,
            verify = verify,
            config = config)
