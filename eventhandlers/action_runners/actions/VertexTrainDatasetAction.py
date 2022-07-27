from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.database.source_control.working_dir import WorkingDir
from google.cloud import aiplatform
from google.oauth2 import service_account
        
class VertexTrainDatasetAction(ActionRunner):
    public_name = 'Vertex Ai Train Dataset'
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

    def execute_action(self, session):
        dir_id = self.action.config_data.get('directory_id')
        dir = WorkingDir.get_by_id(session = session, directory_id=dir_id)

        credentials = service_account.Credentials.from_service_account_info(auth)

        aiplatform.init(
            project='coastal-set-357115',
            location='us-central1',
            credentials=credentials,
            staging_bucket='gs://mandmc-tria-backet',
            experiment='diffgram-vertexai-integration',
            experiment_description='This is trial for diffgram and vertext api integration'
        )

        datasets_list = aiplatform.datasets.ImageDataset.list()

        existing_datasets = []

        for dataset in datasets_list:
            existing_datasets.append(dataset.__dict__['_gca_resource'].__dict__['_pb'].display_name)

        if dir.nickname in existing_datasets:
            print("Here we create a new dataset on the Vertex AI")
        else:
            print("Here we reuse old dataset on Vertex AI")

        pass