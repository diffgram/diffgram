from shared.auth.OAuth2Provider import OAuth2ClientBase
from shared.settings import settings
import requests
import boto3
import base64
from shared.shared_logger import get_shared_logger
import urllib

logger = get_shared_logger()


class CognitoDiffgramClient(OAuth2ClientBase):
    client_id: str
    client_secret: str
    auth_header: str

    def __init__(self):
        self.client_id = settings.OAUTH2_PROVIDER_CLIENT_ID
        if settings.OAUTH2_PROVIDER_CLIENT_SECRET:
            str_credentials = f'{self.client_id}:{self.client_secret}'
            encoded_credentials = base64.b64encode(str_credentials.encode('utf-8'))
            self.auth_header = f'Basic: {encoded_credentials}'

    def get_access_token_with_code_grant(self, code: str) -> dict:
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/token'

        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'code': code,
            'redirect_uri': settings.OAUTH2_DEFAULT_REDIRECT_URL
        }
        response = requests.post(url = url, data = payload)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'Error on cognito {url}: {response.status_code}')
            logger.error(f'{response.text}')

    def revoke(self, refresh_token: str) -> bool:
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/revoke'

        payload = {
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'token': refresh_token,
        }

        response = requests.post(url = url, data = payload)
        if response.status_code == 200:
            logger.info('Token Revoke Success')
            return True
        else:
            logger.error(f'Error on cognito {url}: {response.status_code}')
            logger.error(f'{response.text}')
            return False

    def logout(self, refresh_token) -> str:
        """

        :param refresh_token:
        :return: redirect_url
        """
        if refresh_token:
            revoke_result = self.revoke(refresh_token)
            if not revoke_result:
                logger.error(f'Error on cognito /revoke endpoint. Revoke failed.')
                return None

        url = f'{settings.OAUTH2_PROVIDER_HOST}logout'

        payload = {
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'logout_uri': settings.DEFAULT_LOGIN_URL,
            'response_type': 'code',
        }
        query_params = urllib.parse.urlencode(payload)
        logout_url = f'{url}?{query_params}'
        logger.debug(f'Cognito Logout Url: {logout_url}')
        return logout_url

    def get_user(self, access_token: str) -> dict:
        """
            Get a user from OIDC provider.
        :param access_token: access token that belongs to the user to be fetched..
        :return:
        """
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/userInfo'
        auth_value = f'Bearer {access_token}'
        response = requests.get(url = url, headers = {'Authorization': auth_value})
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'Error on cognito userinfo: {response.status_code}')
            logger.error(f'{response.text}')

    def get_access_token_from_jwt(self, jwt_data: dict):
        """
            Extract the access token from given JWT
        :param jwt_data:
        :return:
        """
        if type(jwt_data) != dict:
            return None
        return jwt_data.get('access_token')

    def get_refresh_token_from_jwt(self, jwt_data: dict):
        """
            Extract the refresh token from given JWT
        :param jwt_data:
        :return:
        """
        if jwt_data is None:
            return None
        return jwt_data.get('refresh_token')

    def refresh_token(self, token: str) -> dict:
        """
            Refresh the current access token
        :param token: the access token to refresh.
        :return: New access token
        """
        url = f'{settings.OAUTH2_PROVIDER_HOST}oauth2/token'

        payload = {
            'grant_type': 'refresh_token',
            'client_id': settings.OAUTH2_PROVIDER_CLIENT_ID,
            'refresh_token': token,
            'redirect_uri': settings.OAUTH2_DEFAULT_REDIRECT_URL
        }
        response = requests.post(url = url, data = payload)
        if response.status_code == 200:
            logger.debug(f'refresh token success {response.json()}')
            return response.json()
        else:
            logger.error(f'Error on cognito {url}: {response.status_code}')
            logger.error(f'{response.text}')

    def get_login_url(self):
        return settings.COGNITO_LOGIN_URL
