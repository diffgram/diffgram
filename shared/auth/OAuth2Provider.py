# OPEN CORE - ADD
from shared.settings import settings
from shared.utils.singleton import Singleton
import time
import abc
import traceback
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


def check_oauth2_setup():
    """
        Initializes Keylcoak client for startup check purposes.
    :return: True if init was successful.
    """
    if settings.USE_OAUTH2:
        logger.info('Testing Keycloak setup...')
        try:
            prov = OAuth2Provider()
            oidc = prov.get_client()
        except Exception as e:
            data = traceback.format_exc()
            logger.error(data)
            logger.error(f'Error connecting setting up Keycloak')
            return None
    return True


class SingletonABC(abc.ABCMeta, Singleton):
    pass


class OAuth2ClientBase(metaclass = SingletonABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'logout') and
                callable(subclass.logout) and
                hasattr(subclass, 'get_user') and
                callable(subclass.get_user) and
                hasattr(subclass, 'get_access_token_from_jwt') and
                callable(subclass.get_access_token_from_jwt) and
                hasattr(subclass, 'refresh_token') and
                callable(subclass.refresh_token) and
                hasattr(subclass, 'get_refresh_token_from_jwt') and
                callable(subclass.get_refresh_token_from_jwt) and
                hasattr(subclass, 'get_access_token_with_code_grant') and
                callable(subclass.get_access_token_with_code_grant) and
                hasattr(subclass, 'get_login_url') and
                callable(subclass.get_login_url) or

                NotImplemented)

    @abc.abstractmethod
    def get_login_url(self, refresh_token: str):
        """
            Logout a user from OIDC Provider.
        :param refresh_token: refresh token to invalidate
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def logout(self, refresh_token: str) -> str:
        """
            Logout a user from OIDC Provider.
        :param refresh_token: refresh token to invalidate
        :return: logout url or None if no external url is used.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, access_token: str):
        """
            Get a user from OIDC provider.
        :param access_token: access token that belongs to the user to be fetched..
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_access_token_from_jwt(self, jwt_data: dict):
        """
            Extract the access token from given JWT
        :param jwt_data:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_refresh_token_from_jwt(self, jwt_data: dict):
        """
            Extract the refresh token from given JWT
        :param jwt_data:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_token(self, token: str) -> dict:
        """
            Refresh the current access token
        :param token: the access token to refresh.
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_access_token_with_code_grant(self, code: str) -> dict:
        """
            Get access token from code grant given on OAuth callback success.
        :param code: the code granted to exchange for an access token.
        :return:
        """
        raise NotImplementedError


class OAuth2Provider(metaclass = Singleton):
    """
        Factory Class For OIDC Clients implementation.
        Depending on the setting set in settings.OIDC_PROVIDER_NAME
        this class will instantiatiate a different client oidc provider implementation for
        users to manage login, registration, token refresh, etc...
    """
    oidc_client: OAuth2ClientBase

    def __init__(self):
        from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
        from shared.auth.CognitoDiffgramClient import CognitoDiffgramClient

        provider = settings.OAUTH2_PROVIDER_NAME

        if not provider:
            raise ValueError("No DIFFGRAM_STATIC_STORAGE_PROVIDER env var set. valid values are [gcp, aws, azure]")

        if provider == 'keycloak':
            self.oidc_client = KeycloakDiffgramClient()
        if provider == 'cognito':
            self.oidc_client = CognitoDiffgramClient()

    def get_client(self):
        return self.oidc_client
