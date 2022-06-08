from methods.regular.regular_api import *
from shared.regular import regular_log
from azure.ai.textanalytics import TextAnalyticsClient
from shared.connection.connectors.connectors_base import Connector
from azure.core.credentials import AzureKeyCredential


def with_azure_exception_handler(f):
    def wrapper(*args):
        log = regular_log.default()
        try:
            return f(*args)
        except Exception as e:
            log['error']['auth_azure_credentials'] = 'Error connecting to Azure. Please ' \
                                                     'check you private secret and id are correct, ' \
                                                     'and that you have the correct pemirssions over your buckets.'
            log['error']['exception_details'] = str(e)
            # return {'log': log}
            raise e

    return wrapper


class AzureConnectorTextAnalytics(Connector):

    def connect(self):
        log = regular_log.default()
        try:
            if 'client_secret' not in self.auth_data:
                log['error']['client_secret'] = 'auth_data must provide client_secret.'
                return log
            if 'endpoint_url' not in self.auth_data:
                log['error']['endpoint_url'] = 'auth_data must provide endpoint_url.'
                return log

            credential_key_AzureKeyCredential = AzureKeyCredential(self.auth_data['client_secret'])
            self.text_analytics_client = TextAnalyticsClient(
                self.auth_data['endpoint_url'], 
                credential_key_AzureKeyCredential)
            
            log['result'] = True
            return log
        except Exception as e:
            log['error']['auth_credentials'] = 'Error connecting to Azure. Please check auth info.'
            log['error']['exception_details'] = str(e)
            return log

    def test_connection(self):
        log = self.connect()
        if len(log['error'].keys()) > 0:
            return {'log' : log}

        return {'log' : log}





