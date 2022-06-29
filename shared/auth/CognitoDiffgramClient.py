from shared.auth.OIDCProvider import OAuth2ClientBase
from shared.settings import settings
import requests
import boto3


class CognitoDiffgramClient(OAuth2ClientBase):

    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', endpoint_url = settings.OAUTH2_PROVIDER_HOST)

    def get_access_token_with_code_grant(self, code: str) -> dict:
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/token'

        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'code': code,
            'redirect_url': settings.Red
        }

        response = requests.post(url = url, json = payload)

        result = response.json()

        return result

    def logout(self, refresh_token):
        url = f'{settings.OAUTH2_PROVIDER_HOST}logout'

        payload = {
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'redirect_uri': f'{settings.URL_BASE}/user/login',
        }

        response = requests.get(url = url, params = payload)
        return response.json()

    def get_user(self, access_token: str) -> dict:
        """
            Get a user from OIDC provider.
        :param access_token: access token that belongs to the user to be fetched..
        :return:
        """
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/userInfo'
        headers = f'Bearer {access_token}'
        response = requests.get(url = url, params = {}, headers = headers)
        return response.json()

    def get_access_token_from_jwt(self, jwt_data: dict):
        """
            Extract the access token from given JWT
        :param jwt_data:
        :return:
        """
        return jwt_data.get('access_token')

    def get_refresh_token_from_jwt(self, jwt_data: dict):
        """
            Extract the refresh token from given JWT
        :param jwt_data:
        :return:
        """
        return jwt_data.get('refresh_token')

    def refresh_token(self, token: str) -> dict:
        """
            Refresh the current access token
        :param token: the access token to refresh.
        :return:
        """
        raise NotImplementedError

    def get_access_token_with_code_grant(self, code: str) -> dict:
        """
            Get access token from code grant given on OAuth callback success.
        :param code: the code granted to exchange for an access token.
        :return:
        """
        raise NotImplementedError
