# OPEN CORE - ADD
from google.cloud import storage
import numpy as np
import sys
import json
import requests, time, tempfile, yaml
from io import BytesIO
from shared.helpers.permissions import get_gcs_service_account
from shared.settings import settings
import boto3
import traceback
from imageio import imread
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class DataToolsGCP:
    """
    These tools are designed to be used on a new thread (not on http request directly)

    Use init with class for ease with google cloud buckets
    Can we use @staticmethod then? I don't think so?se t

    """

    def __init__(self):
        try:
            self.gcs = storage.Client(settings.GOOGLE_PROJECT_NAME)
            self.gcs = get_gcs_service_account(self.gcs)

            # Careful this is the main bucket for web which is different from ML bucket
            self.bucket = self.gcs.get_bucket(settings.CLOUD_STORAGE_BUCKET)

            self.ML_bucket = self.gcs.get_bucket(settings.ML__CLOUD_STORAGE_BUCKET)
        except Exception as exception:
            logger.error('Error intializing GCP Client')
            traceback.print_exc()

    def create_resumable_upload_session(
        self,
        input: 'Input',
        blob_path: str,
        content_type: str = None,
    ):
        """
        Create an upload session url where the user can upload a file to be stored
        in the given blob path.

        :param input: Input object
        :param blob_path: the file path to create the upload session
        :param content_type: Content type of the give blob_path
        :return:
        """

        blob = self.bucket.blob(blob_path)
        url = blob.create_resumable_upload_session(content_type = content_type)
        if input is not None:
            input.resumable_url = url
        return url

    def transmit_chunk_of_resumable_upload(
        self,
        stream,
        blob_path: str,
        prior_created_url: str,
        content_type: str,  # Why do we have to keep redeclaring content type
        content_start: int,
        content_size: int,
        total_size: int,  # total size of whole upload (not chunk),
        total_parts_count: int,
        chunk_index: int,
        input: 'Input',
        batch: 'InputBatch' = None
    ):

        """
        Function job  is to send a request given the url and content byte information
            Conceptually this is very very similar to what we were
            already doing in terms of seeking with a file
            https://github.com/googleapis/google-resumable-media-python/issues/61
            Right so the assumption is the object is being stored

        Assuming / hoping the built in "retry" will work
            for this but can review more later

        From transmit next chunk
            The upload will be considered complete if the stream produces
                fewer than :attr:`chunk_size` bytes when a chunk is read from it.
            ... So we need to have chunk size match the expected chunk right...

        Byte range Inclusive / Exclusive:
            Right now it leaves the start as is (0 indexed)
            And then it subtracts 1 from end.
            So basically the “end byte” is Exclusive and the start byte is Inclusive.

        :param stream: byte stream to send to cloud provider
        :param blob_path: the string indicating the path in the bucket where the bytes will be stored
        :param prior_created_url: The previously created URL
        :param content_type: The content type of the stream
        :param content_start: The content index start
        :param content_size: The chunk size
        :param total_size: The total size of the stream
        :param total_parts_count: The total count of chunks from the stream
        :param chunk_index: The current index to be sent
        :param input: The Diffgram Input object where the parts are stored
        :param batch: If the upload was from a batch upload, the parts will be saved on the batch provided here.
        """

        # - 1 seems to be needed
        # it's "includsive" ?

        end = int(content_start) + int(content_size) - 1

        content_range_extended: str = "bytes " + str(content_start) + \
                                      "-" + str(end) + "/" + str(total_size)

        headers = {"Content-Range": content_range_extended}

        try:
            response = requests.put(
                url = prior_created_url,
                data = stream,
                headers = headers
            )
        except Exception as e:
            raise e
            # TODO if we are going to have a try block
            # here should we error / pass this to Input instance in some way?
            return False

        return response

    def download_from_cloud_to_local_file(self, cloud_uri: str, local_file: str):
        """
            Download a file from the given blob bath to the given local file path
        :param cloud_uri: string for the bucket's path
        :param local_file: string for the local file path to download to.
        :return: File Object that contains the downloaded file
        """

        blob = self.bucket.blob(cloud_uri)
        self.gcs.download_blob_to_file(
            blob_or_uri = blob,
            file_obj = local_file)
        return local_file

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
        blob = self.bucket.blob(blob_path)
        blob.upload_from_filename(temp_local_path,
                                  content_type = content_type,
                                  timeout = timeout)

    def get_image(self, blob_path: str):
        """
            Returns the numpy image of the given blob_path in Cloud Providers's Blob Storage.
        :param blob_path: path of the cloud provider bucket to download the bytes from
        :return: numpy image object for the downloaded image
        """
        blob = self.bucket.blob(blob_path)
        try:
            image_string = blob.download_as_string()
            image_np = imread(BytesIO(image_string))
        except:
            # Default image / icon?
            # TODO prefer some other type of icon here
            # Also not a fan of it saving a full image
            # maybe better to set a flag "couldn't download thumb" or something...
            # ie so if we change icon later...
            image_np = np.zeros([100, 100, 3], dtype = np.uint8)
            image_np.fill(255)

        return image_np

    def upload_from_string(self,
                           blob_path: str,
                           string_data: str,
                           content_type: str,
                           bucket_type: str = "web"):
        """
            Uploads the given string to gcp blob storage service.
        :param blob_path: the blob path where the file will be uploaded in the bucket
        :param string_data: the string data to upload
        :param content_type: content type of the string data
        :param bucket_type: the Diffgram bucket type (either 'web' or 'ml'). Defaults to 'web'
        :return: None
        """

        if bucket_type == "web":
            blob = self.bucket.blob(blob_path)

        if bucket_type == "ml":
            blob = self.ML_bucket.blob(blob_path)

        result = blob.upload_from_string(string_data, content_type = content_type)

    def download_bytes(self, blob_path: str):
        """
            Downloads the given blob as bytes content.
        :param blob_path: path of the cloud provider bucket to download the bytes from
        :return: bytes of the blob that was downloaded
        """
        blob = self.bucket.blob(blob_path)
        image_bytes = blob.download_as_string()
        return image_bytes

    def build_secure_url(self, blob_name: str, expiration_offset: int = None, bucket: str = "web"):
        """
            Builds a presigned URL to access the given blob path.
        :param blob_name: The path to the blob for the presigned URL
        :param expiration_offset: The expiration time for the presigned URL
        :param bucket: string for the bucket type (either 'web' or 'ml') defaults to 'web'
        :return: the string for the presigned url
        """
        if expiration_offset is None:
            expiration_offset = 40368000
        expiration_time = int(time.time() + expiration_offset)

        if bucket == "web":
            blob = self.bucket.blob(blob_name)

        if bucket == "ml":
            blob = self.ML_bucket.blob(blob_name)

        filename = blob_name.split("/")[-1]
        url_signed = blob.generate_signed_url(
            expiration = expiration_time,
            response_disposition = 'attachment; filename=' + filename
        )
        return url_signed

    def get_string_from_blob(self, blob_name: str):
        """
            Gets the data from the given blob path as a string
        :param blob_name: path to the blob on the cloud providers's bucket
        :return: string data of the downloaded blob
        """
        blob = self.ML_bucket.blob(blob_name)

        return blob.download_as_string()

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

        blob = self.bucket.blob(image.url_signed_blob_path)
        image.url_signed = blob.generate_signed_url(expiration = image.url_signed_expiry)

        if hasattr(image, 'url_signed_thumb_blob_path') and image.url_signed_thumb_blob_path:
            blob = self.bucket.blob(image.url_signed_thumb_blob_path)
            image.url_signed_thumb = blob.generate_signed_url(expiration = image.url_signed_expiry)

        session.add(image)

    ############################################################  AI / ML FUNCTIONS ##############################################

    # TODO refactor to be generic item if possible?
    # Potential problem is strings are different

    def build_secure_url_inference(self, session, ai, inference):

        inference.url_signed_expiry = int(time.time() + 2592000)  # 1 month

        dir = ai.ml.blob_dir + "/out/" + str(inference.image.id)

        blob = self.bucket.blob(dir + "_out.jpg")
        inference.processed_image_url = blob.generate_signed_url(
            expiration = inference.url_signed_expiry)

        blob = self.bucket.blob(dir + "_out_thumb.jpg")
        inference.processed_image_url_thumb = blob.generate_signed_url(
            expiration = inference.url_signed_expiry)

        session.add(inference)

    def url_model_update(self, session, version):

        # TODO this name may changed base on AI package

        blob_name = version.ml.blob_dir + "/frozen/frozen_inference_graph.pb"
        version.ml.url_model = self.build_secure_url(
            blob_name,
            600,
            bucket = "ml"
        )
        return version

    def url_tensorboard_update(self, session, version):
        # Careful this returns blob object not name
        blob = list(self.ML_bucket.list_blobs(
            prefix = version.ml.blob_dir + "/events",
            max_results = 1))
        if len(blob) >= 1:
            version.ml.url_tensorboard = self.build_secure_url(
                blob[0].name, 600)
        return version

    def label_dict_builder(
        self,
        file_list
    ):
        """

        Switched to using file.id since the label file is unique
        and makes more sense than extra call to label file

        """

        # Map db ids to id session staring with 123 etc for tensorflow
        file_list.sort(key = lambda x: x.id)

        label_dict = {}
        start_at_1_label = 1
        lowest_label = 0

        # Why are we neding the greater than here?
        # Why not just query unique?
        # Was this a hold over before we knew we had labels specifically?
        # Just feel there should be an easier way to do this

        for file in file_list:
            if file.id > lowest_label:
                label_dict[int(file.id)] = start_at_1_label
                start_at_1_label += 1
                lowest_label = file.id

        return label_dict

    def label_map_new(self, session, ai):

        file_list = ai.get_labels(session = session,
                                  file_type = "label",
                                  ann_is_complete = None)

        label_dict = self.label_dict_builder(
            file_list = file_list)

        # why did we need unique here?
        # Labels_unique = set(Labels)
        # Do we want the label dict to reference the label file
        # OR the original label id?

        ai.ml.label_dict = label_dict
        ai.ml.num_classes = len(file_list)
        session.add(ai)

        out = ""
        for i, file in enumerate(file_list):
            new = "\nitem {"
            id = "\nid: " + str(label_dict[file.id])
            name = "\nname: '" + str(file.label.name) + "'\n }\n"
            out += new + id + name

        blob = self.ML_bucket.blob(ai.ml.blob_dir + "/label_map.pbtext")
        blob.upload_from_string(out, content_type = 'text/pbtext')

        # TODO maybe rename to label_map_job_dir  ? to differentiate between blob and ml job
        ai.ml.label_map_dir = ai.ml.job_dir + "/label_map.pbtext"

        print("Built label_map", file = sys.stderr)

        return "success"

    # TODO refactor internal / external methods for more clarity
    # Could have seperate method to do from working dir
    # This is the iterative update method?

    def yaml_new_internal(self, session, version, project):

        """
        Load existing YAML file
        Do updates
        Save YAML file to version directory
        """
        print("[YAML processor] Started", file = sys.stderr)
        annotations_list = []
        len_images = None

        for image in version.image_file_list:
            if image.soft_delete != True:
                # TODO review test image and done_labelling
                # if image.soft_delete != True and image.is_test_image != True and image.done_labeling == True:
                image_dict = {'blob_name': images_dir + str(image.id),
                              'width': image.width,
                              'height': image.height,
                              'filename': image.original_filename}

                packet = {'packet': {'image': image_dict}}

                if ai.ml.method == "object_detection":
                    box_dict_list = []
                    for box in image.boxes:
                        if box.soft_delete is True:
                            continue
                        if box.label.soft_delete is True:
                            continue
                        box_dict_list.append({'label_id': box.label_id,
                                              'label_name': box.label.name,
                                              'x_min': box.x_min,
                                              'x_max': box.x_max,
                                              'y_min': box.y_min,
                                              'y_max': box.y_max})
                    packet['packet']['boxes'] = box_dict_list

                if ai.ml.method == "semantic_segmentation":
                    if image.mask_joint_blob_name:
                        image_dict['mask_joint_blob_name'] = image.mask_joint_blob_name

                if ai.ml.method == "semantic_segmentation" or ai.ml.sub_method == "mask_rcnn":
                    polygon_dict_list = []
                    for polygon in image.polygons:
                        if polygon.soft_delete is not True:
                            if polygon.label.soft_delete is not True:

                                polygon_dict = {'label_id': polygon.label_id,
                                                'label_name': polygon.label.name,
                                                'x_min': polygon.x_min,
                                                'x_max': polygon.x_max,
                                                'y_min': polygon.y_min,
                                                'y_max': polygon.y_max}

                                if polygon.mask_blob_name:
                                    polygon_dict['mask_blob_name_list'] = polygon.mask_blob_name['list']

                                polygon_dict_list.append(polygon_dict)

                    packet['packet']['polygons'] = polygon_dict_list

                annotations_list.append(packet)

            if counter % 100 == 0:
                print("Percent done", (counter / len_images) * 100, file = sys.stderr)
            counter += 1

        print("annotations_list len", len(annotations_list), file = sys.stderr)

        yaml_data = yaml.dump(annotations_list, default_flow_style = False)
        json_data = json.dumps(annotations_list)
        ai.ml.annotations_string_yaml = ai.ml.blob_dir + "/annotations.yaml"
        ai.ml.annotations_string_json = ai.ml.blob_dir + "/annotations.json"
        session.add(ai)
        blob = self.ML_bucket.blob(ai.ml.annotations_string_yaml)
        blob.upload_from_string(yaml_data, content_type = 'text/yaml')
        blob = self.ML_bucket.blob(ai.ml.annotations_string_json)
        blob.upload_from_string(json_data, content_type = 'text/json')

        print("[YAML processor] Built YAML", file = sys.stderr)
        return "success"

    # OLD TODO refactor to new style
    def categoryMap(session):

        project = get_current_project(session = session)
        version = get_current_version(session = session)
        ml_settings = get_ml_settings(session = session, version = version)
        Labels_db = session.query(Label).filter_by(project_id = project.id).order_by(Label.id.desc())

        Images = session.query(Image).filter_by(version_id = version.id)

        Labels = []

        for i in Labels_db:
            if i.soft_delete != True:
                Labels.append(i)

        Labels_unique = set(Labels)

        Labels.sort(key = lambda x: x.id)
        label_dict = {}
        start_at_1_label = 1
        lowest_label = 0
        for label in Labels:
            if label_id > lowest_label:
                label_dict[label_id] = start_at_1_label
                start_at_1_label += 1
                lowest_label = label_id

        project_str = str(project.id) + "/" + str(version.id) + "/ml/" + str(ml_settings.ml_compute_engine_id)
        project_str += "/label_map.pbtext"

        categoryMap = {}
        for i, c in enumerate(Labels_unique):
            name = str(c.name)
            id = int(label_dict[int(c.id)])

            dict = {'id': int(i + 1), 'name': name}
            categoryMap[id] = dict

        return categoryMap
