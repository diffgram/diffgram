# OPENCORE - ADD
import boto3

from .s3_connector import regular_log
from .s3_connector import S3Connector
from shared.data_tools_core_minio import DataToolsMinio

class MinioConnector(S3Connector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "minio"

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_id' not in self.auth_data:
                log['error']['client_id'] = 'auth_data must provide a client_id.'
                return {'log': log}
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide minio_access_key_id and minio_secret_access_key .'
                return {'log': log}
            if 'endpoint_url' not in self.auth_data or not self.auth_data['endpoint_url']:
                log['error']['endpoint_url'] = 'auth_data must provide minio_endpoint_url.'
                return {'log': log}

            self.connection_client = DataToolsMinio.get_client(
                endpoint_url=self.auth_data['endpoint_url'],
                access_key_id=self.auth_data['client_id'],
                secret_access_key=self.auth_data['client_secret'],
                verify=False if self.auth_data['disabled_ssl_verify'] else None)
            
            return {'result': True}
        except Exception as e:
            log['error'][
                'auth_credentials'] = 'Error connecting to MinIO. Please check your connection values.'
            return {'log': log}
