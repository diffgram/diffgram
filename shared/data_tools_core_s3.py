# OPEN CORE - ADD
import time
from io import BytesIO
from shared.settings import settings
import boto3
import mimetypes

from imageio import imread


class DataToolsS3:
    """
    These tools are designed to be used on a new thread (not on http request directly)

    Use init with class for ease with google cloud buckets
    Can we use @staticmethod then? I don't think so?se t

    """

    def __init__(self):

        self.s3_client = boto3.client('s3',
                                      aws_access_key_id = settings.DIFFGRAM_AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key = settings.DIFFGRAM_AWS_ACCESS_KEY_SECRET)
        self.s3_bucket_name = settings.DIFFGRAM_S3_BUCKET_NAME
        self.s3_bucket_name_ml = settings.ML__DIFFGRAM_S3_BUCKET_NAME

    def create_resumable_upload_session(
            self,
            input: object,
            blob_path: str,
            content_type: str = None
    ):
        """
            Creates an S3 Multipart upload session and attached the upload ID
            to the Diffgram Input Object for future reference.
        """
        mimetypes.init()
        if content_type is None:
            content_type = mimetypes.guess_type(input.original_filename)[0]
        response = self.s3_client.create_multipart_upload(
            ACL = 'private',
            Bucket = self.s3_bucket_name,
            Key = blob_path,
            ContentType = content_type
        )
        input.upload_aws_id = response['UploadId']

    def transmit_chunk_of_resumable_upload(
            self,
            stream,
            blob_path: str,
            prior_created_url: str,
            content_type: str,  # Why do we have to keep redeclaring content type
            content_start: int,
            content_size: int,
            total_size: int,  # total size of whole upload (not chunk)
            total_parts_count: int,
            chunk_index: int,
            input: object,
            batch: object = None

    ):
        """
                basic concept
        is to send a request given the url and content byte information
            Conceptually this is very very similar to what we were
            already doing in terms of seeking with a file

            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.initiate_multipart_upload
        Right so the assumption is the object is being stored

        Assuming / hoping the built in "retry" will work
        for this but can review more later

        From transmit next chunk
        Assumes ``chunk_size`` is not :data:`None` on the current blob.
        :param stream:
        :param blob_path:
        :param prior_created_url:
        :param content_type:
        :param content_start:
        :param content_size:
        :param total_size:
        :param total_parts_count:
        :param chunk_index:
        :param input:
        :return:
        """
        # - 1 seems to be needed
        # it's "includsive" ?

        part = self.s3_client.upload_part(
            Body = stream,
            Bucket = self.s3_bucket_name,
            Key = blob_path,
            UploadId = input.upload_aws_id,
            PartNumber = int(chunk_index) + 1)
        if input:
            if input.upload_aws_parts_list is None or \
                    input.upload_aws_parts_list.get('parts') is None:
                input.upload_aws_parts_list = {
                    'parts': [{"PartNumber": int(chunk_index) + 1, "ETag": part["ETag"]}]
                }
            else:
                input.upload_aws_parts_list['parts'].append(
                    {"PartNumber": int(chunk_index) + 1, "ETag": part["ETag"]}
                )
        elif not input and batch:
            if batch.upload_aws_parts_list is None or \
                    batch.upload_aws_parts_list.get('parts') is None:
                batch.upload_aws_parts_list = {
                    'parts': [{"PartNumber": int(chunk_index) + 1, "ETag": part["ETag"]}]
                }
            else:
                batch.upload_aws_parts_list['parts'].append(
                    {"PartNumber": int(chunk_index) + 1, "ETag": part["ETag"]}
                )

        if int(chunk_index) == int(total_parts_count) - 1:
            result = self.s3_client.complete_multipart_upload(
                Bucket = self.s3_bucket_name,
                Key = blob_path,
                UploadId = input.upload_aws_id if input else batch.upload_aws_id,
                MultipartUpload = {"Parts": input.upload_aws_parts_list['parts'] if input else batch.upload_aws_parts_list['parts']}
            )
        return True

    def download_from_cloud_to_local_file(self, cloud_uri, local_file):
        self.s3_client.download_fileobj(self.s3_bucket_name, cloud_uri, local_file)
        return local_file

    def upload_to_cloud_storage(
            self,
            temp_local_path: str,
            blob_path: str,
            content_type: str = None,
            timeout = None
    ):
        """
        TODO this assumes this operation was successful
        would like some better error handling here...
        """
        self.s3_client.upload_file(temp_local_path, self.s3_bucket_name, blob_path,
                                   ExtraArgs = {'ContentType': content_type})

    def upload_from_string(self, blob_path, string_data, content_type, bucket_type = "web"):
        if bucket_type == "web":
            bucket_name = self.s3_bucket_name

        if bucket_type == "ml":
            bucket_name = self.s3_bucket_name_ml

        self.s3_client.put_object(Body = string_data,
                                  Bucket = bucket_name,
                                  Key = blob_path,
                                  ContentType = content_type)

    def download_bytes(self, blob_path):

        bytes_buffer = BytesIO()
        self.s3_client.download_fileobj(Bucket = self.s3_bucket_name, Key = blob_path, Fileobj = bytes_buffer)
        byte_value = bytes_buffer.getvalue()
        return byte_value

    def get_image(self, blob_path):

        bytes_buffer = BytesIO()
        self.s3_client.download_fileobj(Bucket = self.s3_bucket_name, Key = blob_path, Fileobj = bytes_buffer)
        byte_value = bytes_buffer.getvalue()
        # image_string = byte_value.decode('utf-8')  # python3, default decoding is utf-8

        image_np = imread(BytesIO(byte_value))


        return image_np


    # TODO clarify this is for file downloads not images / maybe refactor
    def build_secure_url(self, blob_name, expiration_offset = None, bucket = "web"):
        """
        blob_name, string of blob name. don't include CLOUD_STORAGE_BUCKET
        expiration_offset, integer, additional time from this moment to allow link
        """

        if expiration_offset is None:
            expiration_offset = 40368000

        expiration_time = expiration_offset

        if bucket == "web":
            bucket_name = self.s3_bucket_name

        if bucket == "ml":
            bucket_name = self.s3_bucket_name_ml

        filename = blob_name.split("/")[-1]

        signed_url = self.s3_client.generate_presigned_url('get_object',
                                                           Params = {
                                                            'Bucket': bucket_name,
                                                            'ResponseContentDisposition': 'attachment; filename=' + filename,
                                                            'Key': blob_name},
                                                           ExpiresIn = int(expiration_time))
        return signed_url

    def get_string_from_blob(self, blob_name):
        """
        blob_name, string of blob name. don't include CLOUD_STORAGE_BUCKET
        """
        raise NotImplementedError

    def rebuild_secure_urls_image(self, session, image):
        """
            Re created the signed url for the given image object.
            This function is usually used in the context of an image url expiring
            and needing to get a new url.
        :param session:
        :param image:
        :return:
        """
        image.url_signed_expiry = int(time.time() + 2592000)

        image.url_signed = self.build_secure_url(image.url_signed_blob_path, expiration_offset = 2592000)

        if hasattr(image, 'url_signed_thumb_blob_path') and image.url_signed_thumb_blob_path:
            image.url_signed_thumb = self.build_secure_url(image.url_signed_thumb_blob_path, expiration_offset = 2592000)
        session.add(image)
    # TODO refactor to be generic item if possible?
    # Potential problem is strings are different

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

    # TODO would like to try @profile on this for testing memory stuff

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
