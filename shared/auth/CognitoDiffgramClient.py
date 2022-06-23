from shared.auth.OIDCProvider import OIDCClientBase
from shared.settings import settings
import requests
import boto3


class CognitoDiffgramClient(OIDCClientBase):

    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', endpoint_url=settings.OIDC_PROVIDER_HOST)

    def get_access_token_with_code_grant(self, code: str) -> dict:
        url = f'{settings.OIDC_PROVIDER_HOST}oauth2/token'

        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.OIDC_PROVIDER_CLIENT_ID,
            'code': code,
            'redirect_url': settings.Red
        }

        response = requests.post(url = url, json = payload)

        result = response.json()

    als