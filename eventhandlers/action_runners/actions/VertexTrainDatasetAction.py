from action_runners.base.ActionRunner import ActionRunner
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.annotation.instance import Instance
from shared.database.source_control.file import File
from shared.database.action.action_run import ActionRun
from shared.data_tools_core import Data_tools
from shared.data_tools_core_gcp import DataToolsGCP
from shared.shared_logger import get_shared_logger

from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.google_cloud_storage_connector import VertexAIConnector

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
        run = ActionRun.get_latest_action_status(self.session, self.action.id)
        if run != None and run.status == 'running':
            return False
        return True

    def execute_action(self, session):
        ActionRun.set_action_run_status(self.session, self.action_run.id, "running")
        temp_folder_name = f"temp_{self.action_run.id}"

        self.bucket_name = self.action.config_data.get('staging_bucket_name_without_gs_prefix')
        self.model_name = self.action.config_data.get('model_name')

        connection_strategy = ConnectionStrategy(
            connection_class = VertexAIConnector,
            connection_id = self.action.config_data.get('connection_id')['id'],
            session = self.session
        )

        [vertex_ai_connector, success] = connection_strategy.get_connector()

        if not success:
            ActionRun.set_action_run_status(self.session, self.action_run.id, "failed")
            return {
                "success": False,
                "error": "Not able to connect to Vertex AI"
            }

        experiment = "experiment"
        experiment_description = "Experiment run from Diffgram"

        if self.action.config_data.get('experiment'):
            experiment = self.action.config_data.get('experiment')

        if self.action.config_data.get('experiment_description'):
            experiment_description = self.action.config_data.get('experiment_description')
        
        vertex_ai_instance_details = {
            "location": "us-central1",
            "staging_bucket_name": self.bucket_name,
            "experiment": experiment,
            "experiment_description": experiment_description
        }
        
        vertex_ai_connector.init_ai_platform(vertex_ai_instance_details)
        gcp_data_tools = self.init_gcp_data_tools(vertex_ai_connector)
        file_list = self.get_file_list(session)

        dataset_file_list = self.migrate_files_to_gcp(file_list, gcp_data_tools, temp_folder_name)

        if len(dataset_file_list) == 0:
            ActionRun.set_action_run_status(self.session, self.action_run.id, "failed")
            return {
                "success": False,
                "error": "No file in the dataset"
            }

        self.count_dataset_labels(session, dataset_file_list)
        vertexai_import_file = self.write_vertex_format_jsonl_file(gcp_data_tools, temp_folder_name, dataset_file_list)
        
        self.clean_up_temp_dir(temp_folder_name)
        
        vertex_ai_connector.create_vertex_ai_dataset(self.model_name, vertexai_import_file)

        model_type = "MOBILE_TF_VERSATILE_1"
        if (self.action.config_data.get('autoML_model')):
            model_type = self.action.config_data.get('autoML_model')['value']

        budget_milli_node_hours=20000

        if self.action.config_data.get('training_node_hours') is not None:
            budget_milli_node_hours = int(self.action.config_data.get('training_node_hours')) * 1000

        model_id = vertex_ai_connector.train_automl_model(self.model_name, model_type, budget_milli_node_hours)
        
        ActionRun.set_action_run_status(self.session, self.action_run.id, "finished")

        return {
            "success": True,
            "model_name": self.model_name,
            "model_id": model_id
        }

    def get_file_list(self, session) -> list:
        directory_id = self.action.config_data.get('directory_id')
        self.directory = WorkingDir.get_by_id(session = session, directory_id=directory_id)
        file_list = WorkingDirFileLink.file_list(session=session, working_dir_id=self.directory.id, limit=None)

        return file_list

    def migrate_files_to_gcp(self, file_list, gcp_data_tools, temp_folder_name) -> list:
        dataset_file_list = []
        for file in file_list:
            if file.image is not None:
                file_link = self.write_diffgram_blob_to_gcp(gcp_data_tools, temp_folder_name, file)
                dataset_file_list.append({
                    "filename": f"gs://{self.bucket_name}/{file_link}",
                    "diffgram_file": file
                })

        return dataset_file_list

    def build_vertex_format_instance(self, instance, session, file) -> dict:
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

    def build_vertexai_instance_file_instance_array(self, file, session) -> list:
        vertex_format_instance_list = []
        instance_list = Instance.list(session=session, file_id=file['diffgram_file'].id)

        for instance in instance_list:
            vertex_format_instance = self.build_vertex_format_instance(instance, session, file['diffgram_file'])
            if vertex_format_instance is not None:
                vertex_format_instance_list.append(vertex_format_instance)

        return vertex_format_instance_list

    def write_vertex_format_jsonl_file(self, gcp_data_tools, temp_folder_name, file_list) -> str:
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

        gcp_data_tools.upload_to_cloud_storage(f"{temp_folder_name}/{filename}", f"{self.model_name}/{filename}")
        self.clean_up_temp_file(f"{temp_folder_name}/{filename}")

        return f"gs://{self.bucket_name}/{self.model_name}/{filename}"

    def init_gcp_data_tools(self, google_vertex_connector) -> dict:
        bucket_config = {
            "GOOGLE_PROJECT_NAME": self.action.config_data.get('gcp_project_id'),
            "CLOUD_STORAGE_BUCKET": self.bucket_name,
            "ML__CLOUD_STORAGE_BUCKET": self.bucket_name,
            "credentials": google_vertex_connector.get_credentials()
        }

        gcp_data_tools = DataToolsGCP(bucket_config)

        return gcp_data_tools

    def write_diffgram_blob_to_gcp(self, gcp_data_tools, temp_folder_name, file) -> str:
        blob_bytes = data_tools.download_bytes(file.image.url_signed_blob_path)
        filename = file.image.original_filename

        local_path = f"{temp_folder_name}/{filename}"
        upload_path = f"{self.model_name}/{filename}"

        try:
            os.makedirs(temp_folder_name)
        except OSError:
            pass

        with open(local_path, "wb") as binary_file:
            binary_file.write(blob_bytes)

        gcp_data_tools.upload_to_cloud_storage(local_path, upload_path, "image")
        self.clean_up_temp_file(local_path)

        return upload_path

    def count_dataset_labels(self, session, file_list) -> dict:
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