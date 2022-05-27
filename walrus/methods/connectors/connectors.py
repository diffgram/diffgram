# OPENCORE - ADD
from abc import ABC, abstractmethod
import inspect
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from shared.connection.connection_operations import Connection_Operations


class ConnectorManager:
    CONNECTIONS_MAPPING = {
        'google_gcp': 'GoogleCloudStorageConnector',
        'microsoft_azure': 'AzureConnector',
        'amazon_aws': 'S3Connector',
        'labelbox': 'LabelboxConnector',
        'datasaur': 'DatasaurConnector',
        'scale_ai': 'ScaleAIConnector',
        'minio': 'MinioConnector'
    }

    def __init__(self, connection=None, session=None, integration_name=None):
        if connection is None:
            self.session = session
            self.connector_key = self.CONNECTIONS_MAPPING[integration_name]

        else:
            connector_key = connection.integration_name
            self.connection = connection
            self.session = session
            self.connector_key = self.CONNECTIONS_MAPPING[connector_key]

    def get_connector_class(self):
        # get a handle on the module
        package_dir = Path(__file__).resolve().parent
        for (_, module_name, _) in iter_modules([package_dir]):
            # Exclude all test modules
            if 'test' in module_name:
                continue
            # import the module and iterate through its attributes
            modules = [import_module(f"methods.connectors.{module_name}")]
            for module in modules:
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)

                    if isclass(attribute):
                        # Add the class to this package's variables
                        globals()[attribute_name] = attribute

        return globals()[self.connector_key]

    def get_connector_instance(self):
        connector_class = self.get_connector_class()
        connection_operations = Connection_Operations(
            session=self.session,
            member=None,
            connection_id=self.connection.id
        )
        connection_operations.get_existing_connection(self.connection.id)
        auth_data = {
            'client_email': self.connection.account_email,
            'client_id': self.connection.private_id,
            'client_secret': connection_operations.get_secret(),
            'project_id': self.connection.project_id_external
        }
        config_data = {'project_string_id': self.connection.project.project_string_id}
        connector = connector_class(auth_data=auth_data, config_data=config_data)
        return connector
