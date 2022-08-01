from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.database.source_control.working_dir import WorkingDir, WorkingDirFileLink
from shared.database.annotation.instance import Instance
from shared.database.source_control.file import File
from google.cloud import aiplatform

from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.google_cloud_storage_connector import GoogleCloudStorageConnector

# GCP auth example
        # auth = {
        #     "project_id": "project id",
        #     "private_key_id": "prokect_key_id",
        #     "private_key": "priveate key",
        #     "client_email": "cliend email",
        #     "client_id": "client if",
        #     "token_uri": "https://oauth2.googleapis.com/token"
        # }

# Sudo code
#         - Get directory that was chosen for action
#         - Get all files objects from that directory
#         - Get all the file instances (format is here: https://cloud.google.com/vertex-ai/docs/datasets/prepare-image?hl=en_US&_ga=2.163634871.-945446037.1653695686&_gac=1.187635162.1658943405.Cj0KCQjwxIOXBhCrARIsAL1QFCaQ0nAU08M_3wqaG0gDVPfWwPz2v0ne5HkrokPSSvkXFog0Gl97QcoaAhYQEALw_wcB#json-lines_2)
#         - Convert instances to the bounding boxes
#         - Download files to the temp folder and then send it to GCP with newly created bund boxes

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
    completion_condition_data = ActionCompleteCondition(default_event = 'some_diffgram_event',
                                                        event_list = ['some_diffgram_event'])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True


    def get_file_list(self, session):

        directory_id = self.action.config_data.get('directory_id')
        directory = WorkingDir.get_by_id(session = session, directory_id=directory_id)
        file_list = WorkingDirFileLink.file_list(session=session, working_dir_id=directory.id, limit=None)

        return file_list


    def build_vertex_format_instance(self, instance, session):
        label = File.get_by_id(session=session, 
                               file_id=instance.label_file_id)
        vertex_format_instance = {
            "displayName": label.label.name,
            "xMin": instance.x_min,
            "xMax": instance.x_max,
            "yMin": instance.y_min,
            "yMax": instance.y_max
        }
        return vertex_format_instance



    def build_vertex_format_jsonl_file(self, file_list, session):

        export_data = []

        for file in file_list:
            vertex_format_instance_list = []
            instance_list = Instance.list(session=session, file_id=file.id)

            for instance in instance_list:
                vertex_format_instance = self.build_vertex_format_instance(instance, session)
                vertex_format_instance_list.append(vertex_format_instance)

            # TODO load bucket from connection
            # TODO load file list from original filename
            single_file = {
                "imageGcsUri": "gs://mandmc-tria-backet/3 (10).JPG",
                "boundingBoxAnnotations": vertex_format_instance_list
            }

            print(single_file)

        export_data.append(single_file)
        return export_data

    def write_vertex_format_jsonl_file(self, export_data):

        # TODO write to temporary bytes

        with open(F'google_format_{time.time()}.jsonl', 'w') as outfile:
            for entry in export_data:
                json.dump(entry, outfile)
                outfile.write('\n')

        # TODO upload this file to cloud storage using connection


    def init_ai_platform(self):
        aiplatform.init(
            project = self.action.config_data.get('gcp_project_name'),
            location = self.action.config_data.get('location'),
            credentials = self.credentials,
            staging_bucket = 'gs://' + self.action.config_data.get('staging_bucket_name_without_gs_prefix'),
            experiment = self.action.config_data.get('experiment'),
            experiment_description = self.action.config_data.get('experiment_description')
        )


    def execute_action(self, session):

        connection_strategy = ConnectionStrategy(
            connection_class = GoogleCloudStorageConnector,
            connector_id = connector_id,
            session = self.session)

        google_vertex_connector = connection_strategy.get_connector()
        credentials = google_vertex_connector.get_credentials()

        file_list = self.get_file_list(session)
        export_data = self.build_vertex_format_jsonl_file(file_list, session)
        self.write_vertex_format_jsonl_file(export_data)

        self.init_ai_platform()

        datasets_list = aiplatform.datasets.ImageDataset.list()

        existing_datasets = []

        for dataset in datasets_list:
            existing_datasets.append(dataset.__dict__['_gca_resource'].__dict__['_pb'].display_name)

        working_dataset = None
        if directory.nickname not in existing_datasets:
            working_dataset = aiplatform.ImageDataset.create(
                display_name=directory.nickname,
                gcs_source=['gs://mandmc-tria-backet/3 (10).JPG', 'gs://mandmc-tria-backet/3 (870).JPG'],
                import_schema_uri=aiplatform.schema.dataset.ioformat.image.bounding_box,
                data_item_labels=image_annotation #this is throwing error and I'm not sure why
                # the type sepcified is dict: https://github.com/googleapis/python-aiplatform/blob/main/google/cloud/aiplatform/datasets/image_dataset.py#L42
            )
            print("New dataset has been created on Vertex AI")
        else:
            dataset_index = existing_datasets.index(directory.nickname)
            working_dataset = datasets_list[dataset_index]

        print(working_dataset)
        pass