from shared.regular.regular_api import *  # Import regular_api from shared package

from action_runners.base.ActionRunner import ActionRunner  # Import ActionRunner base class
from shared.database.action.action_template import Action_Template  # Import Action_Template class
from action_runners.base.ActionTrigger import ActionTrigger  # Import ActionTrigger class
from action_runners.base.ActionCondition import ActionCondition  # Import ActionCondition class
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition  # Import ActionCompleteCondition class
from shared.database.source_control.file import File  # Import File class

from shared.connection.connection_strategy import ConnectionStrategy  # Import ConnectionStrategy class
from shared.connection.microsoft_azure_text_analytics import AzureConnectorTextAnalytics  # Import AzureConnectorTextAnalytics class
from shared.ingest import packet  # Import packet from shared.ingest

class AzureTextAnalyticsSentimentAction(ActionRunner):
    # Class for Azure Text Analytics Sentiment Analysis Action Runner

    # Class attributes
    public_name = 'Azure Text Analytics'
    description = 'Azure Text Analytics'
    icon = 'https://www.svgrepo.com/show/375442/healthcare-nlp-api.svg'
    kind = 'azure_sentiment'
    trigger_data = ActionTrigger(default_event='input_file_uploaded', event_list=[])  # Trigger data for the action
    precondition = ActionCondition(default_event=None, event_list=[])  # Precondition for the action
    completion_condition_data = ActionCompleteCondition(default_event='action_completed', event_list=[])  # Completion condition data

    def execute_pre_conditions(self, session) -> bool:
        # Method to execute pre-conditions
        return True

    def test_execute_action(self, session, file_id, connection_id):
        # Method for testing the execution of the action
        pass

    def execute_action(self, session):
        # Method to execute the sentiment analysis action
        file_id = self.event_data['file_id']  # Get file_id from event data
        if not file_id:
            logger.warning(f'Action has no file_id Stopping execution')
            return

        file = File.get_by_id(session, file_id=file_id)  # Get the file object

        raw_text = file.text_file.get_text()  # Get the raw text from the file

        documents = [raw_text]  # Prepare the documents for sentiment analysis

        connection_strategy = ConnectionStrategy(
            connection_class=AzureConnectorTextAnalytics,
            connector_id=connector_id,
            session=self.session)  # Create a connection strategy

        text_analytics_client = connection_strategy.get_client()  # Get the Text Analytics client

        response = text_analytics_client.analyze_sentiment(documents, language="en")  # Perform sentiment analysis

        result = [doc for doc in response if not doc.is_error]  # Filter out error responses

        # Save annotations
        mock_external_map = {
            "negative": {89: {display_name: "neutral", id: 241, name: 242}},
            "positive": {89: {display_name: "neutral", id: 240, name: 242}},
            "neutral": {89: {display_name: "neutral", id: 242, name: 242}}
        }

        instance_list = []
        for doc in result:
            # Process the sentiment analysis results and create instance_list
            pass

        if do_save_annotations is True:
            packet.enqueue_packet(
                session=session,
                media_url=None,
                media_type='text',
                file_id=file.id,
                instance_list=instance_list,
                commit_input=True,
                mode="update")

            return True
