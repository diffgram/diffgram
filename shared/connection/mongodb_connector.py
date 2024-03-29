import traceback
from shared.regular.regular_api import *
from shared.connection.connectors.connectors_base import Connector, with_connection
from shared.regular import regular_log
from pymongo import MongoClient
from bson import ObjectId

def with_mongodb_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            return f(*args)
        except Exception as e:
            log['error']['exception_details'] = str(e)
            return {'log': log}

    return wrapper


class MongoDBConnector(Connector):
    url_signer_service: str or None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "mongo_db"

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide a client_secret.'
                return {'log': log}

            self.connection_client = MongoClient(self.auth_data.get('client_secret'))
            return {'result': True}
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to Mongo DB. Please check you connection URL is correct.'
            return {'log': log}

    @with_connection
    @with_mongodb_exception_handler
    def __get_db_list(self, opts):
        """

        :param opts:
        :return:
        """
        # List the available databases
        database_names = self.connection_client.list_database_names()

        # Print the database names
        result = []
        for db_name in database_names:
            result.append(db_name)
        return {'data': result}

    @with_connection
    @with_mongodb_exception_handler
    def __list_collections_from_db(self, opts):
        """Upload a file to diffgram from an S3 bucket

        :param s3_file_key: path of file to fetch from
        :return: file obj if file was uploaded, else False
        """
        spec_list = [{'db_name': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}

        database = input['db_name']
        # Select the database
        db = self.connection_client[database]

        # List the collections (tables) in the database
        collection_names = db.list_collection_names()
        return {'data': collection_names}

    @with_connection
    @with_mongodb_exception_handler
    def __get_documents(self, opts):
        """
            Get documents from a collection
        :param opts:
        :return:
        """
        spec_list = [{'db_name': str},
                     {'collection_name': str},
                     {'exclude_id_list': {'required': False, 'type': list, 'allow_empty': True}},
                     {'reference_id': str}]
        log = regular_log.default()
        log, input = regular_input.input_check_many(untrusted_input = opts,
                                                    spec_list = spec_list,
                                                    log = log)
        if len(log["error"].keys()) >= 1:
            return {'log': log}

        database = input['db_name']
        collection_name = input['collection_name']
        exclude_id_list = input['exclude_id_list']
        reference_id = input['reference_id']
        # Select the database
        db = self.connection_client[database]
        collection = db[collection_name]
        query = {}
        if exclude_id_list:
            if reference_id == '_id':
                exclude_id_list = [ObjectId(id) for id in exclude_id_list]
            query[reference_id] = {'$nin': exclude_id_list}
        items = collection.find(query)
        return {'data': list(items)}

    def test_connection(self):
        auth_result = self.connect()
        if 'log' in auth_result:
            return auth_result
        try:
            # Test mongo db connection with a small admin command
            self.connection_client.admin.command('ismaster')

        except Exception as e:
            log = regular_log.default()
            log['error']['connection'] = 'Error connecting to MongoDB. Please check you connection url is correct.'
            log['error']['details'] = traceback.format_exc()
            return {'log': log}
        return auth_result

    @with_connection
    def get_meta_data(self):
        return {}

    @with_connection
    def fetch_data(self, opts):
        """
            This function routes any action_type to the correct S3 connector actions.
        :return: Object
        """
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'get_db_list':
            return self.__get_db_list(opts)
        if action_type == 'list_collections_from_db':
            return self.__list_collections_from_db(opts)
        if action_type == 'get_documents':
            return self.__get_documents(opts)

    @with_connection
    def put_data(self, opts):
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'send_export':
            return self.__send_export(opts)
