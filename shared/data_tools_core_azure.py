# OPEN CORE - ADD
import time
from io import BytesIO
from shared.settings import settings
import mimetypes
from azure.storage.blob import BlobBlock, BlobServiceClient, ContentSettings, StorageStreamDownloader
from azure.storage.blob._models import BlobSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
import base64
import uuid
import datetime
from imageio import imread


class DataToolsAzure:
    """
    These tools are designed to be used on a new thread (not on http request directly)

    Use init with class for ease with google cloud buckets
    Can we use @staticmethod then? I don't think so?se t

    """

    def __init__(self):
        self.azure_service_client = BlobServiceClient.from_connection_string(settings.DIFFGRAM_AZURE_CONNECTION_STRING)
        self.azure_container_name = settings.DIFFGRAM_AZURE_CONTAINER_NAME
        self.azure_container_name_ml = settings.ML__DIFFGRAM_AZURE_CONTAINER_NAME

    def create_resumable_upload_session(
        self,
        input: 'Input',
        blob_path: str,
        content_type: str = None
    ):
        """
          Azure has no concept of creating a resumable session, so for now this does nothing.
        """
        return

    def transmit_chunk_of_resumable_upload(
        self,
        stream,
        blob_path: str,
        prior_created_url: str,
        content_type: str,
        content_start: int,
        content_size: int,
        total_size: int,
        total_parts_count: int,
        chunk_index: int,
        input: 'Input',
        batch: 'InputBatch' = None

    ):
        """
        This functions creates and append a block to the block list for a block upload
        with the azure sdk. We need to generate a block ID per block and store on our input
        object.

        From transmit next chunk
        Assumes ``chunk_size`` is not :data:`None` on the current blob.
        :param stream: byte stream to send to cloud provider
        :param blob_path: the string indicating the path in the bucket where the bytes will be stored
        :param prior_created_url: The previously created URL (NOT used for Azure)
        :param content_type: The content type of the stream (NOT used for Azure)
        :param content_start: The content index start (NOT used for Azure)
        :param content_size: The chunk size (NOT used for Azure)
        :param total_size: The total size of the stream (NOT used for Azure)
        :param total_parts_count: The total count of chunks from the stream
        :param chunk_index: The current index to be sent
        :param input: The Diffgram Input object where the parts are stored
        :param batch: If the upload was from a batch upload, the parts will be saved on the batch provided here.
        :return:
        """
        # - 1 seems to be needed
        # it's "includsive" ?
        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name, blob = blob_path)

        block_id = str(uuid.uuid4())
        blob_client.stage_block(block_id = block_id, data = stream)
        if input:
            if input.upload_azure_block_list is None or input.upload_azure_block_list.get(
                'upload_azure_block_list') is None:
                input.upload_azure_block_list = {
                    'upload_azure_block_list': [block_id]
                }
            else:
                new_list = input.upload_azure_block_list['upload_azure_block_list'].copy()
                new_list.append(block_id)
                input.upload_azure_block_list = {'upload_azure_block_list': new_list}
        elif batch and not input:
            if batch.upload_azure_block_list is None or batch.upload_azure_block_list.get(
                'upload_azure_block_list') is None:
                batch.upload_azure_block_list = {
                    'upload_azure_block_list': [block_id]
                }
            else:
                new_list = batch.upload_azure_block_list['upload_azure_block_list'].copy()
                new_list.append(block_id)
                batch.upload_azure_block_list = {'upload_azure_block_list': new_list}
        if int(chunk_index) == int(total_parts_count) - 1:
            # Build blocks list
            blocks = []
            if input:
                for block in input.upload_azure_block_list['upload_azure_block_list']:
                    blocks.append(BlobBlock(block_id = block))
                blob_client.commit_block_list(blocks)
            elif not input and batch:
                for block in batch.upload_azure_block_list['upload_azure_block_list']:
                    blocks.append(BlobBlock(block_id = block))
                blob_client.commit_block_list(blocks)
        return True

    def download_from_cloud_to_local_file(self,
                                          cloud_uri: str,
                                          local_file: str):
        """
            Download a file from the given blob bath to the given local file path
        :param cloud_uri: string for the bucket's path
        :param local_file: string for the local file path to download to.
        :return: File Object that contains the downloaded file
        """

        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                blob = cloud_uri)
        download_stream = blob_client.download_blob()
        local_file.write(download_stream.readall())

    def upload_to_cloud_storage(
        self,
        temp_local_path: str,
        blob_path: str,
        content_type: str = None,
        timeout: int = None
    ):
        """
            Uploads the file in the given path to the Cloud Provider's storage service.
        :param temp_local_path: path of the local file to upload
        :param blob_path: path in the bucket where the blobl will be uploaded
        :param content_type: content type of the blob to upload
        :param timeout: Timeout for upload (optional)
        :return: None
        """
        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                blob = blob_path)
        my_content_settings = ContentSettings(content_type = content_type)

        with open(temp_local_path, "rb") as stream:
            blob_client.upload_blob(stream, overwrite = True, content_settings = my_content_settings)

    def upload_from_string(self,
                           blob_path: str,
                           string_data: str,
                           content_type: str,
                           bucket_type: str = "web"):
        """
            Uploads the given string to azure blob storage service.
        :param blob_path: the blob path where the file will be uploaded in the bucket
        :param string_data: the string data to upload
        :param content_type: content type of the string data
        :param bucket_type: the Diffgram bucket type (either 'web' or 'ml'). Defaults to 'web'
        :return: None
        """
        if bucket_type == 'web':
            blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                    blob = blob_path)
        elif bucket_type == 'ml':
            blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name_ml,
                                                                    blob = blob_path)
        else:
            raise Exception('Invalid bucket_type, must be either web or ml.')
        my_content_settings = ContentSettings(content_type = content_type)
        blob_client.upload_blob(string_data, content_settings = my_content_settings)

    def download_bytes(self, blob_path: str):
        """
            Downloads the given blob as bytes content.
        :param blob_path: path of the cloud provider bucket to download the bytes from
        :return: bytes of the blob that was downloaded
        """

        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                blob = blob_path)
        download_stream = blob_client.download_blob()

        return download_stream.content_as_bytes()

    def get_image(self, blob_path: str):
        """
            Returns the numpy image of the given blob_path in Cloud Providers's Blob Storage.
        :param blob_path: path of the cloud provider bucket to download the bytes from
        :return: numpy image object for the downloaded image
        """
        bytes_buffer = BytesIO()
        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                blob = blob_path)
        download_stream = blob_client.download_blob()

        byte_value = download_stream.content_as_bytes()
        # image_string = byte_value.decode('utf-8')  # python3, default decoding is utf-8

        image_np = imread(BytesIO(byte_value))
        return image_np

    def build_secure_url(self, blob_name: str, expiration_offset: int = None, bucket: str = "web"):
        """
            Builds a presigned URL to access the given blob path.
        :param blob_name: The path to the blob for the presigned URL
        :param expiration_offset: The expiration time for the presigned URL
        :param bucket: string for the bucket type (either 'web' or 'ml') defaults to 'web'
        :return: the string for the presigned url
        """
        container = None
        if bucket == 'web':
            container = self.azure_container_name
        elif bucket == 'ml':
            container = self.azure_container_name_ml
        else:
            raise Exception('Invalid bucket type provided. Must be either "web" or "ml"')
        shared_access_signature = BlobSharedAccessSignature(
            account_name = self.azure_service_client.account_name,
            account_key = self.azure_service_client.credential.account_key
        )
        if expiration_offset is None:
            expiration_offset = 40368000

        added_seconds = datetime.timedelta(0, expiration_offset)
        expiry_time = datetime.datetime.utcnow() + added_seconds
        filename = blob_name.split("/")[-1]
        sas = shared_access_signature.generate_blob(
            container_name = container,
            blob_name = blob_name,
            start = datetime.datetime.utcnow(),
            expiry = expiry_time,
            permission = BlobSasPermissions(read = True),
            content_disposition = 'attachment; filename=' + filename,
        )
        sas_url = 'https://{}.blob.core.windows.net/{}/{}?{}'.format(
            self.azure_service_client.account_name,
            container,
            blob_name,
            sas
        )
        return sas_url

    def get_string_from_blob(self, blob_name: str):
        """
            Gets the data from the given blob path as a string
        :param blob_name: path to the blob on the cloud providers's bucket
        :return: string data of the downloaded blob
        """
        blob_client = self.azure_service_client.get_blob_client(container = self.azure_container_name,
                                                                blob = blob_name)
        download_stream = blob_client.download_blob()

        return download_stream.content_as_text()

    def rebuild_secure_urls_image(self, session: 'Session', image: 'Image'):
        """
            Re creates the signed url for the given image object.
            This function is usually used in the context of an image url expiring
            and needing to get a new url.
        :param session: the sqlalchemy DB session
        :param image: the Diffgram Image() object
        :return: None
        """
        image.url_signed_expiry = int(time.time() + 2592000)

        image.url_signed = self.build_secure_url(image.url_signed_blob_path, expiration_offset = 2592000)

        if hasattr(image, 'url_signed_thumb_blob_path') and image.url_signed_thumb_blob_path:
            image.url_signed_thumb = self.build_secure_url(image.url_signed_thumb_blob_path,
                                                           expiration_offset = 2592000)
        session.add(image)

    ############################################################  AI / ML FUNCTIONS ##############################################
    def build_secure_url_inference(self, session, ai, inference):
        raise NotImplementedError

    def url_model_update(self, session, version):
        # TODO this name may changed base on AI package

        raise NotImplementedError

    def url_tensorboard_update(self, session, version):
        raise NotImplementedError

    def create_tf_example(self,
                          file,
                          label_dict,
                          project_id,
                          sub_method = "default"
                          ):
        """
        Create a tf example for use with object detection api
        This includes optional masks using mask rcnn
        """
        raise NotImplementedError

    def create_tf_example_deep_lab_citiscape(
        self,
        file,
        project_id
    ):
        raise NotImplementedError

    def tf_records_new(
        self,
        session,
        file_list,
        project_id,
        method,
        output_blob_dir,
        sub_method = None,
        label_dict = None
    ):
        raise NotImplementedError

    def label_dict_builder(
        self,
        file_list
    ):
        """

        Switched to using file.id since the label file is unique
        and makes more sense than extra call to label file

        """
        raise NotImplementedError

    def label_map_new(self, session, ai):
        raise NotImplementedError

    # TODO refactor internal / external methods for more clarity
    # Could have seperate method to do from working dir
    # This is the iterative update method?

    def yaml_new_internal(self, session, version, project):
        """
        Load existing YAML file
        Do updates
        Save YAML file to version directory
        """
        raise NotImplementedError

    # OLD TODO refactor to new style
    def categoryMap(session):
        raise NotImplementedError
