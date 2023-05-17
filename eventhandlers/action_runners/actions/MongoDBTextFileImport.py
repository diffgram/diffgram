from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.connection.connection_strategy import ConnectionStrategy
from shared.shared_logger import get_shared_logger
logger = get_shared_logger()

class MongoDBTextFileImportAction(ActionRunner):
    public_name = 'Mongo DB Text Import'
    description = 'Import Text files into Diffgram from your Mongo DB connection.'
    icon = 'https://miro.medium.com/v2/resize:fit:512/1*doAg1_fMQKWFoub-6gwUiQ.png'
    kind = 'MongoDBTextFileImport'  # The kind has to be unique to all actions
    category = 'import'  # Optional
    precondition = ActionCondition(default_event = None, event_list = [])
    # What events can this action listen to?
    trigger_data = ActionTrigger(default_event = 'time_trigger',
                            event_list = ['time_trigger'])

    # How to declare the actions as completed?
    completion_condition_data = ActionCompleteCondition(default_event = 'some_diffgram_event',
                                                        event_list = ['some_diffgram_event'])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        """
            Queries a mongodb collection for all its documents and adds them into diffgram.
        :param session:
        :return:
        """
        connection_id = self.action.config_data.get('connection_id')
        if connection_id is None:
            logger.error('No connection_id provided in event_data')
            return
        connector, success = ConnectionStrategy(session = session).get_connector(connection_id)
        if not success:
            logger.error('Error getting connector: {}'.format(connector))
            return
        # Add relevant data to opts
        connection_result = connector.connect()
        if 'log' in connection_result:
            logger.error('Error connecting to MongoDB: {}'.format(connection_result['log']))

        connector.fetch_data(opts = {
            'action_type': 'get_documents',
            'event_data': {
                'collection_name': self.action.config_data.get('collection_name'),
                'db_name': self.action.config_data.get('db_name'),
            }
        })