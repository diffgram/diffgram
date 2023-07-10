from action_runners.base.ActionRunner import ActionRunner
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.connection.connection_strategy import ConnectionStrategy
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.file import File
from shared.database.batch.batch import InputBatch
from shared.shared_logger import get_shared_logger
from shared.regular import regular_log
from shared.ingest.packet import enqueue_packet
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
    completion_condition_data = ActionCompleteCondition(default_event = None,
                                                        event_list = [])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def get_existing_reference_ids(self, session, directory_id: int) -> list:
        """
            Returns a list of existing reference ids for this dir id
            .
        :param session:
        :return:
        """
        result = []
        files_metadata = session.query(File.file_metadata, File.id)\
            .join(WorkingDirFileLink, File.id == WorkingDirFileLink.file_id)\
            .filter(WorkingDirFileLink.working_dir_id == directory_id,
                    File.state != "removed").all()

        for item in files_metadata:
            metadata = item[0]
            if metadata is None:
                continue
            if metadata.get('reference_id') is None:
                continue
            result.append(metadata['reference_id'])

        return result
    def validate_data(self) -> dict:
        log = regular_log.default()
        connection = self.action.config_data.get('connection')
        if connection is None:
            msg = 'No connection_id provided in config_data'
            logger.error(msg)
            log['error']['connection_id'] = msg
            return log

        # Get directory ID
        directory_id = self.action.config_data.get('directory_id')
        if directory_id is None:
            msg = 'No directory_id provided in config_data'
            logger.error(msg)
            log['error']['directory_id'] = msg
            return log
        # Get Database name
        db_name = self.action.config_data.get('db_name')
        if db_name is None:
            msg = 'No db_name provided in config_data'
            logger.error(msg)
            log['error']['db_name'] = msg
            return log
        # Get Collection name
        collection_name = self.action.config_data.get('collection_name')
        if collection_name is None:
            msg = 'No collection_name provided in config_data'
            logger.error(msg)
            log['error']['collection_name'] = msg
            return log
        # Get collection key mappings
        key_mappings = self.action.config_data.get('key_mappings')
        if key_mappings.get('file_name') is None:
            msg = 'Missing keymapping for file_name'
            logger.error(msg)
            log['error']['key_mappings.file_name'] = msg
            return log
        if key_mappings.get('reference_id') is None:
            msg = 'Missing keymapping for reference_id'
            logger.error(msg)
            log['error']['key_mappings.reference_id'] = msg
            return log
        if key_mappings.get('text_data') is None:
            msg = 'Missing keymapping for text_data'
            logger.error(msg)
            log['error']['key_mappings.text_data'] = msg
            return log
        return log
    def execute_action(self, session):
        """
            Queries a mongodb collection for all its documents and adds them into diffgram.
        :param session:
        :return:
        """
        log = self.validate_data()
        if regular_log.log_has_error(log):
            return
        connection = self.action.config_data.get('connection')
        connector, success = ConnectionStrategy(session = session).get_connector(connection.get('id'), check_perms = False)

        if not success:
            msg = 'Error getting connector: {}'.format(connector)
            logger.error(msg)
            return


        ids_to_exclude = self.get_existing_reference_ids(session,
                                                         directory_id = self.action.config_data.get('directory_id'))

        # Add relevant data to opts
        connection_result = connector.connect()
        if 'log' in connection_result:
            logger.error('Error connecting to MongoDB: {}'.format(connection_result['log']))

        result = connector.fetch_data({
            'action_type': 'get_documents',
            'event_data': {},
            'collection_name': self.action.config_data.get('collection_name'),
            'reference_id': self.action.config_data['key_mappings']['reference_id'],
            'db_name': self.action.config_data.get('db_name'),
            'exclude_id_list': ids_to_exclude,
        })
        if 'log' in result:
            logger.error('Error fetching data from MongoDB: {}'.format(result['log']))
            return
        documents_to_upload = result['data']
        batch = InputBatch.new(session = session, project_id = self.action.project_id)
        for document in documents_to_upload:
            text_data_key = self.action.config_data['key_mappings']['text_data']
            file_name_key = self.action.config_data['key_mappings']['file_name']
            ref_id_key = self.action.config_data['key_mappings']['reference_id']
            text_data = document.get(text_data_key, None)
            file_name = document.get(file_name_key, None)
            document_id = document.get(ref_id_key, None)
            if not text_data:
                logger.warning(f'Skipping document with no text data {document}')
                continue
            if not file_name:
                logger.warning(f'Skipping document with no file_name {document}')
                continue
            diffgram_input = enqueue_packet(project_string_id = self.action.project.project_string_id,
                                            session = session,
                                            media_type = 'text',
                                            directory_id = self.action.config_data.get('directory_id'),
                                            original_filename = file_name,
                                            batch_id = batch.id,
                                            type = 'from_text_data',
                                            text_data = text_data,
                                            mode = "",
                                            file_metadata = {
                                                'reference_id': str(document_id),
                                            },
                                            member = self.action.member_created)
            logger.debug('Enqueued packet {}'.format(diffgram_input))