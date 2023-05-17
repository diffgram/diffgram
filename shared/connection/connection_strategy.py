import datetime
from shared.database.user import User
from dataclasses import dataclass, field

from shared.connection.connection_operations import Connection_Operations

from shared.connection.google_cloud_storage_connector import GoogleCloudStorageConnector, VertexAIConnector
from shared.connection.azure_connector import AzureConnector
from shared.connection.s3_connector import S3Connector
from shared.connection.minio_connector import MinioConnector
from shared.connection.labelbox_connector import LabelboxConnector
from shared.connection.mongodb_connector import MongoDBConnector

CONNECTIONS_MAPPING = {
    'google_gcp': GoogleCloudStorageConnector,
    'microsoft_azure': AzureConnector,
    'amazon_aws': S3Connector,
    'mongo_db': MongoDBConnector,
    'minio': MinioConnector,
    'labelbox': LabelboxConnector,
    'vertex_ai': VertexAIConnector
}


@dataclass()
class ConnectionStrategy:

    def __init__(self,
                 session = None,
                 connection_class = None,
                 connection = None,
                 connection_id = None,
                 integration_name = None):

        self.connection = connection
        self.session = session
        self.integration_name = integration_name
        self.connection_class = connection_class

        if connection_id:
            self.set_connection(connection_id = connection_id, check_perms = False)

    def __post_init__(self):
        if not self.connection_class:
            self.set_connection()

    def set_class(self):
        # The Context is that for some of the storage ones with similar patterns we use the strategy pattern
        # For other classes we still want to follow the connection and test pattern
        # But Already know the class so can just pass it at setup
        # This also removes need to add all to strategy mapping unless good reason like with storage where pattern is so similar

        if self.connection_class:
            return

        if self.integration_name:
            self.connection_class = CONNECTIONS_MAPPING[self.integration_name]
        else:
            self.connection_class = CONNECTIONS_MAPPING[self.connection.integration_name]

    def get_client(self):
        if not self.connection:
            raise Exception("connection object or connection_id must be supplied at init")

        connector, success = self.get_connector()

        connector.connect()

        return connector.get_client()

    def set_connection(self, connection_id = None, check_perms = None):
        if not connection_id: return

        self.connection_operations = Connection_Operations(
            session = self.session,
            member = None,
            connection_id = connection_id
        )
        self.connection = self.connection_operations.get_existing_connection(connection_id)
        if check_perms:
            self.connection_operations.validate_existing_connection_id_permissions()

    def build_auth_data(self, input = None):
        if input and input.get('integration_name'):
            self.integration_name = input.get('integration_name')

        auth_data = {
            'endpoint_url': self.connection.private_host,
            'client_email': self.connection.account_email,
            'client_id': self.connection.private_id,
            'client_secret': self.connection_operations.get_secret(),
            'disabled_ssl_verify': self.connection.disabled_ssl_verify,
            'project_id': self.connection.project_id_external,
            'aws_v4_signature': self.connection.aws_v4_signature,
            'aws_region': self.connection.aws_region,
            'url_signer_service': self.connection.url_signer_service,
        }
        auth_data_to_input = {
            'endpoint_url': 'private_host',
            'client_email': 'account_email',
            'client_id': 'private_id',
            'client_secret': 'private_secret',
            'project_id': 'project_id_external',
            'aws_v4_signature': 'aws_v4_signature',
            'aws_region': 'aws_region',
            'url_signer_service': 'url_signer_service',

        }
        if input:
            for key, value in auth_data.items():
                input_value = input.get(auth_data_to_input.get(key))
                if input_value:
                    auth_data[key] = input_value

        return auth_data

    def get_connector(self, connection_id = None, input = None, check_perms = True):
        """
            input is a Diffgram input dict, overrides preset values
            Process
            1. Gets database connection object
            2. Updates data based in input overrides if applicable
            3. Sets abstract class
            4. Instantiates class

            If the connection is already available as an object check_perms is not 
            expected to do anything.
        """

        self.set_connection(connection_id, check_perms)

        if len(self.connection_operations.log["error"].keys()) >= 1:
            return self.connection_operations.log, False

        auth_data = self.build_auth_data(input)
        config_data = {'project_string_id': self.connection.project.project_string_id}

        self.set_class()
        connector_instance = self.connection_class(auth_data = auth_data, config_data = config_data)

        return connector_instance, True

    @staticmethod
    def add_event_data_to_input(input, session, connection_id):
        user = User.get_current_user(session)
        input['opts']['event_data'] = {
            'request_user': user.id,
            'date_time': datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
            'connection_id': connection_id
        }
        return input
