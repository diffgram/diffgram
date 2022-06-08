
from shared.connection.connection_operations import Connection_Operations

from shared.connection.google_cloud_storage_connector import GoogleCloudStorageConnector
from shared.connection.azure_connector import AzureConnector
from shared.connection.s3_connector import S3Connector
from shared.connection.minio import MinioConnector
from shared.connection.labelbox_connector import LabelboxConnector
from shared.connection.microsoft_azure_text_analytics import AzureConnectorTextAnalytics


CONNECTIONS_MAPPING = {
    'google_gcp': GoogleCloudStorageConnector,
    'microsoft_azure': AzureConnector,
    'amazon_aws': S3Connector,
    'labelbox': LabelboxConnector, 
    'minio': MinioConnector,
    'microsoft_azure_text_analytics': AzureConnectorTextAnalytics,
}

class ConnectionStrategy:

    def __init__(self, connection=None, session=None, integration_name=None):
        self.connection = connection
        self.session = session
        self.integration_name = integration_name


    def set_class():
        if self.integration_name:
            self.connector_class = CONNECTIONS_MAPPING[self.integration_name]
        else:
            self.connector_class = CONNECTIONS_MAPPING[connection.integration_name]


    def set_connection(self, connector_id, check_perms):
        self.connection_operations = Connection_Operations(
            session=self.session,
            member=None,
            connection_id=connector_id
        )
        self.connection = connection_operations.get_existing_connection(connector_id)
        if check_perms:
            self.connection_operations.validate_existing_connection_id_permissions()


    def build_auth_data(self, input=None):
        if input and input.get('integration_name'):
            self.integration_name = input.get('integration_name')

        auth_data = {
            'endpoint_url': input.get('private_host') if input.get('private_host') is not None else self.connection.private_host,
            'client_email':  input.get('account_email') if input.get('account_email') is not None else self.connection.account_email,
            'client_id': input.get('private_id') if input.get('private_id') is not None else self.connection.private_id,
            'client_secret': input.get('private_secret') if input.get('private_secret') is not None else self.connection_operations.get_secret(),
            'disabled_ssl_verify': input.get('disabled_ssl_verify') if input.get('disabled_ssl_verify') is not None else self.connection.disabled_ssl_verify,
            'project_id': input.get('project_id_external') if input.get('project_id_external') is not None else self.connection.project_id_external,
        }
        return auth_data


    def get_connector(self, connector_id=None, input=None, check_perms=True):
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

        self.set_connection(connector_id, check_perms)

        if len(self.connection_operations.log["error"].keys()) >= 1:
            return self.connection_operations.log, False

        auth_data = self.build_auth_data(input)
        config_data = {'project_string_id': self.connection.project.project_string_id}
        
        self.set_class()
        connector_instance = self.connector_class(auth_data=auth_data, config_data=config_data)

        return connector_instance, True


    @staticmethod
    def add_event_data_to_input(input, session, connector_id):
        user = User.get_current_user(session)
        input['opts']['event_data'] = {
            'request_user': user.id,
            'date_time': datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
            'connection_id': connector_id
        }
        return input
