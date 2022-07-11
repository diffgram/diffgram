from shared.regular.regular_api import *

from action_runners.base.ActionRunner import ActionRunner
from shared.database.action.action_template import Action_Template
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.database.source_control.file import File

from shared.connection.connection_strategy import ConnectionStrategy
from shared.connection.microsoft_azure_text_analytics import AzureConnectorTextAnalytics
from shared.ingest import packet


class AzureTextAnalyticsSentimentAction(ActionRunner):
    public_name = 'Azure Text Analytics'
    description = 'Azure Text Analytics'
    icon = 'https://www.svgrepo.com/show/375442/healthcare-nlp-api.svg'
    kind = 'azure_sentiment'
    trigger_data = ActionTrigger(default_event = 'input_file_uploaded', event_list = [])
    precondition = ActionCondition(default_event = None, event_list = [])
    completion_condition_data = ActionCompleteCondition(default_event = 'action_completed', event_list = [])

    def execute_pre_conditions(self, session) -> bool:
        return True

    def test_execute_action(self, session, file_id, connection_id):
        pass

    def execute_action(self, session):
        """
            Executes text analytics sentiment analysis for the file in the event data.
        :param session:
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

        connection_strategy = ConnectionStrategy(
            connection_class = AzureConnectorTextAnalytics,
            connector_id = connector_id,
            session = self.session)

        text_analytics_client = connection_strategy.get_client()

        response = text_analytics_client.analyze_sentiment(documents, language = "en")

        result = [doc for doc in response if not doc.is_error]

        # Save annotations

        # Call ExternalMap
        # Bit of an odd one in mocking global attribute map.
        mock_external_map = {
            "negative": {89: {display_name: "neutral", id: 241, name: 242}},
            "positive": {89: {display_name: "neutral", id: 240, name: 242}},
            "neutral": {89: {display_name: "neutral", id: 242, name: 242}}
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
                # 'name': mock_external_map[doc.sentiment],
                # 'start_sentence': instance['sidS'],
                # 'end_sentence': instance['sidE'],
                # 'start_token': instance['s'],
                # 'end_token': instance['e'],
                # 'start_char': instance['charS'],
                # 'end_char': instance['charE'],
                # 'sentence': sentence['id'],
                'type': 'global',
                'attribute_groups': mock_external_map[doc.sentiment]
            })

        if do_save_annotations is True:
            packet.enqueue_packet(
                session = session,
                media_url = None,
                media_type = 'text',
                file_id = file.id,
                instance_list = instance_list,
                commit_input = True,
                mode = "update")

            return True