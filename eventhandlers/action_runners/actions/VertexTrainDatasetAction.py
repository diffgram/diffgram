from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.annotation.instance import Instance
from shared.database.source_control.file import File
from shared.database.action.action_run import ActionRun
from shared.data_tools_core import Data_tools
from shared.data_tools_core_gcp import DataToolsGCP
from shared.shared_logger import get_shared_logger

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import trainingjob

from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.google_cloud_storage_connector import GoogleCloudStorageConnector

import gc
import shutil
import time
import os
import json

logger = get_shared_logger()

data_tools = Data_tools().data_tools
class VertexTrainDatasetAction(ActionRunner):
    public_name = 'Vertex AI Train Dataset (Google / GCP)'
    description = 'Train model with Vertex AI'
    icon = 'https://www.svgrepo.com/show/375510/vertexai.svg'
    precondition = ActionCondition(default_event = None, event_list = [])
    kind = 'VertexTrainDatasetAction'  # The kind has to be unique to all actions
    category = 'training'  # Optional

    # What events can this action listen to?
    trigger_data = ActionTrigger(default_event = 'manual_trigger',
                            event_list = ['manual_trigger'])

    # What pre-conditions can this action have?
    condition_data = ActionCondition(default_event = 'some_diffgram_event',
                                     event_list = ['some_diffgram_event'])

    # How to declare the actions as completed?
    completion_condition_data = ActionCompleteCondition(default_event = 'action_completed',
                                                        event_list = ['action_completed'])

    def execute_pre_conditions(self, session) -> bool:
        status = ActionRun.get_latest_action_status(self.session, self.action.id)
        if status == 'running':
            return False
        return True

    def execute_action(self, session):
        ActionRun.set_action_run_status(self.session, self.action_run.id, "running")
        temp_folder_name = f"temp_{self.action_run.id}"

        connection_strategy = ConnectionStrategy(
            connection_class = GoogleCloudStorageConnector,
            connection_id = self.action.config_data.get('connection_id'),
            session = self.session
        )

        [google_vertex_connector, success] = connection_strategy.get_connector()

        if not success:
            return
        
        credentials = google_vertex_connector.get_credentials()
        
        self.init_ai_platform(credentials)
        gcp_data_tools = self.init_gcp_data_tools(credentials)

        file_list = self.get_file_list(session)

        dataset_file_list = []
        for file in file_list[:50]:
            if file.image is not None:
                file_link = self.write_diffgram_blob_to_gcp(gcp_data_tools, temp_folder_name, file)
                dataset_file_list.append({
                    "filename": f"gs://{self.action.config_data.get('staging_bucket_name_without_gs_prefix')}/{file_link}",
                    "diffgram_file": file
                })

        self.count_dataset_labels(session, dataset_file_list)
        vertexai_import_file = self.write_vertex_format_jsonl_file(gcp_data_tools, temp_folder_name, dataset_file_list)

        self.clean_up_temp_dir(temp_folder_name)

        datasets_list = aiplatform.datasets.ImageDataset.list()
        existing_datasets = []

        for dataset in datasets_list:
            existing_datasets.append(dataset.__dict__['_gca_resource'].__dict__['_pb'].display_name)

        working_dataset = None
        if self.action.config_data.get('model_name') in existing_datasets:
            dataset_index = existing_datasets.index(self.action.config_data.get('model_name'))
            working_dataset = datasets_list[dataset_index]

            working_dataset.delete()

        working_dataset = aiplatform.ImageDataset.create(
            display_name=f"{self.action.config_data.get('model_name')}",
            gcs_source=vertexai_import_file,
            import_schema_uri=aiplatform.schema.dataset.ioformat.image.bounding_box,
        )

        response = self.train_automl_model(credentials, working_dataset)
        
        ActionRun.set_action_run_status(self.session, self.action_run.id, "finished")

        return {
            "success": True
        }


    def get_file_list(self, session):

        directory_id = self.action.config_data.get('directory_id')
        self.directory = WorkingDir.get_by_id(session = session, directory_id=directory_id)
        file_list = WorkingDirFileLink.file_list(session=session, working_dir_id=self.directory.id, limit=None)

        return file_list


    def build_vertex_format_instance(self, instance, session, file):
        label = File.get_by_id(session=session, 
                               file_id=instance.label_file_id)

        image_height = file.image.height
        image_width = file.image.width
        if label is not None and self.label_count.get(label.label.name) > 10:
            vertex_format_instance = {
                "displayName": label.label.name,
                "xMin": instance.x_min/image_width,
                "xMax": instance.x_max/image_width,
                "yMin": instance.y_min/image_height,
                "yMax": instance.y_max/image_height
            }
            return vertex_format_instance

    def build_vertexai_instance_file_instance_array(self, file, session):
        vertex_format_instance_list = []
        instance_list = Instance.list(session=session, file_id=file['diffgram_file'].id)

        for instance in instance_list:
            vertex_format_instance = self.build_vertex_format_instance(instance, session, file['diffgram_file'])
            if vertex_format_instance is not None:
                vertex_format_instance_list.append(vertex_format_instance)

        return vertex_format_instance_list

    def write_vertex_format_jsonl_file(self, gcp_data_tools, temp_folder_name, file_list):
        filename = f"{time.time()}.jsonl"
        
        with open(f"{temp_folder_name}/{filename}", 'w') as outfile:
            for entry in file_list:
                payload = {
                    "imageGcsUri": f"{entry['filename']}",
                    "boundingBoxAnnotations": self.build_vertexai_instance_file_instance_array(entry, self.session),
                    "dataItemResourceLabels": {
                        "aiplatform.googleapis.com/ml_use": "training"
                    }
                }
                json.dump(payload, outfile)
                outfile.write('\n')

        gcp_data_tools.upload_to_cloud_storage(f"{temp_folder_name}/{filename}", f"{self.action.config_data.get('model_name')}/{filename}")
        self.clean_up_temp_file(f"{temp_folder_name}/{filename}")

        return f"gs://{self.action.config_data.get('staging_bucket_name_without_gs_prefix')}/{self.action.config_data.get('model_name')}/{filename}"

    def init_ai_platform(self, credentials):
        aiplatform.init(
            credentials = credentials,
            project = self.action.config_data.get('gcp_project_id'),
            location = self.action.config_data.get('location'),
            staging_bucket = 'gs://' + self.action.config_data.get('staging_bucket_name_without_gs_prefix'),
            experiment = self.action.config_data.get('experiment'),
            experiment_description = self.action.config_data.get('experiment_description')
        )

    def init_gcp_data_tools(self, credentials):
        bucket_config = {
            "GOOGLE_PROJECT_NAME": self.action.config_data.get('gcp_project_id'),
            "CLOUD_STORAGE_BUCKET": self.action.config_data.get('staging_bucket_name_without_gs_prefix'),
            "ML__CLOUD_STORAGE_BUCKET": self.action.config_data.get('staging_bucket_name_without_gs_prefix'),
            "credentials": credentials
        }

        gcp_data_tools = DataToolsGCP(bucket_config)

        return gcp_data_tools

    def write_diffgram_blob_to_gcp(self, gcp_data_tools, temp_folder_name, file):
        blob_bytes = data_tools.download_bytes(file.image.url_signed_blob_path)
        filename = file.image.original_filename

        try:
            os.makedirs(temp_folder_name)
        except OSError:
            pass

        with open(f"{temp_folder_name}/{filename}", "wb") as binary_file:
            binary_file.write(blob_bytes)

        gcp_data_tools.upload_to_cloud_storage(f"{temp_folder_name}/{filename}", f"{self.action.config_data.get('model_name')}/{filename}", "image")
        self.clean_up_temp_file(f"{temp_folder_name}/{filename}")

        return f"{self.action.config_data.get('model_name')}/{filename}"

    def count_dataset_labels(self, session, file_list):
        label_count = {}

        for file in file_list:
            instance_list = Instance.list(session=session, file_id=file['diffgram_file'].id)
            for instance in instance_list:
                label = File.get_by_id(session=session, file_id=instance.label_file_id)
                if label is not None:
                    if label_count.get(label.label.name) == None:
                        label_count[label.label.name] = 1
                    else:
                        label_count[label.label.name] += 1
        
        self.label_count = label_count
        return label_count

    def train_automl_model(self, credentials, dataset):
        created_dataset_name = dataset.__dict__['_gca_resource'].__dict__['_pb'].name
        id_separator_index = created_dataset_name.rindex('/')
        created_dataset_id = created_dataset_name[id_separator_index + 1:]

        client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
        client = aiplatform.gapic.PipelineServiceClient(client_options=client_options, credentials=credentials)

        training_task_inputs = trainingjob.definition.AutoMlImageObjectDetectionInputs(
            model_type="CLOUD_HIGH_ACCURACY_1",
            budget_milli_node_hours=20000,
            disable_early_stopping=False,
        ).to_value()

        training_pipeline = {
            "display_name": self.action.config_data.get('model_name'),
            "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_object_detection_1.0.0.yaml",
            "training_task_inputs": training_task_inputs,
            "input_data_config": {
                "dataset_id": created_dataset_id
            },
            "model_to_upload": {
                "display_name": self.action.config_data.get('model_name')
            },
        }

        parent = f"projects/{dataset.__dict__['project']}/locations/{dataset.__dict__['location']}"

        response = client.create_training_pipeline(
            parent=parent, 
            training_pipeline=training_pipeline
        )

        return response

    def clean_up_temp_file(self, filename):
        gc.collect()
        try:
            os.remove(filename)
            logger.info("File removed succesfully successfully")
        except OSError as exc:
            logger.error(f"shutil error {str(exc)}")
            pass

    def clean_up_temp_dir(self, path):
        gc.collect()
        try:
            shutil.rmtree(path)  # delete directory
            logger.info("Cleaned successfully")
        except OSError as exc:
            logger.error(f"shutil error {str(exc)}")
            pass