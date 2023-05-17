# OPENCORE - ADD
import boto3
import traceback
import threading
import io
import requests
import urllib.parse

import mimetypes
from shared.regular.regular_api import *
from shared.auth.OAuth2Provider import OAuth2Provider
from shared.helpers import sessionMaker
from shared.database.project import Project
from shared.database.auth.member import Member
from shared.connection.connectors.connectors_base import Connector, with_connection
from shared.ingest import packet
from pathlib import Path
from shared.export.export_view import export_view_core
from shared.database.export import Export
from shared.export.export_utils import generate_file_name_from_export, check_export_permissions_and_status
from shared.regular import regular_log
from pymongo import MongoClient
from shared.data_tools_core_s3 import DataToolsS3
from botocore.config import Config
from shared.ingest.allowed_ingest_extensions import images_allowed_file_names, videos_allowed_file_names


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
        print('ASDAS', self.auth_data)
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

    @with_connection
    def put_data(self, opts):
        if 'action_type' not in opts:
            raise Exception('Provide action_type key.')
        if 'event_data' not in opts:
            raise Exception('Provide event_data key.')
        action_type = opts.pop('action_type')
        if action_type == 'send_export':
            return self.__send_export(opts)
