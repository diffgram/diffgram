from eventhandlers.action_runners.ActionRunner import ActionRunner
from shared.shared_logger import get_shared_logger
from shared.database.task.job.job import Job
from shared.helpers.sessionMaker import session_scope
from shared.utils import job_dir_sync_utils
from shared.database.source_control.file import File
from shared.utils.sync_events_manager import SyncEventManager
from shared.database.source_control.working_dir import WorkingDir
from shared.database.auth.member import Member
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from methods.input.packet import enqueue_packet

logger = get_shared_logger()


class AzureTextAnalyticsAction(ActionRunner):
    def execute_pre_conditions(self, session) -> bool:
        return True

    def execute_action(self, session):
        """
                   Creates a task from the given file_id in the given task template ID.
               :return:
               """
        file_id = self.event_data['file_id']
        if not file_id:
            logger.warning(f'Action has no file_id Stopping execution')
            return

        file = File.get_by_id(session, file_id = file_id)

        raw_text = file.text_file.get_text()
        # or could get tokens etc

        documents = [raw_text]

        # Actual Prediction
        response = text_analytics_client.analyze_sentiment(documents, language="en")
        result = [doc for doc in response if not doc.is_error]

        # Save annotations

        # Call ExternalMap
        # Bit of an odd one in mocking global attribute map.
        mock_external_map = {
            "negative" : {89 : {display_name: "neutral", id: 241, name: 242}},
            "positive" : {89 : {display_name: "neutral", id: 240, name: 242}},
            "neutral": {89 : {display_name: "neutral", id: 242, name: 242}}
            }

        instance_list = []
        for doc in result:
            print("Overall sentiment: {}".format(doc.sentiment))
            print("Scores: positive={}; neutral={}; negative={} \n".format(
                doc.confidence_scores.positive,
                doc.confidence_scores.neutral,
                doc.confidence_scores.negative,
            ))
            instance_list.append({
                #'name': mock_external_map[doc.sentiment],
                #'start_sentence': instance['sidS'],
                #'end_sentence': instance['sidE'],
                #'start_token': instance['s'],
                #'end_token': instance['e'],
                #'start_char': instance['charS'],
                #'end_char': instance['charE'],
                #'sentence': sentence['id'],
                'type': 'global',
                'attribute_groups': mock_external_map[doc.sentiment]
            })

        # For tracking and flexbility 
        enqueue_packet(
            session=session,
            media_url=None,
            media_type='text',
            file_id=file.id,
            instance_list=instance_list,
            commit_input=True,
            mode="update")
        