# OPEN CORE - ADD
from shared.settings import settings
from shared.utils.singleton import Singleton
import time
import abc


class SingletonABC(abc.ABCMeta, Singleton):
    pass


class OIDCClientBase(metaclass = SingletonABC):
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
                callable(subclass.get_access_token_with_code_grant) or

                NotImplemented)

    @abc.abstractmethod
    def logout(self, refresh_token: str):
        """
            Logout a user from OIDC Provider.
        :param refresh_token: refresh token to invalidate
        :return:
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


class OIDCProvider(metaclass = Singleton):
    """
        Factory Class For OIDC Clients implementation.
        Depending on the setting set in settings.OIDC_PROVIDER_NAME
        this class will instantiatiate a different client oidc provider implementation for
        users to manage login, registration, token refresh, etc...
    """
    oidc_client: OIDCClientBase

    def __init__(self):
        from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient

        provider = settings.OIDC_PROVIDER_NAME

        if not provider:
            raise ValueError("No DIFFGRAM_STATIC_STORAGE_PROVIDER env var set. valid values are [gcp, aws, azure]")

        if provider == 'keycloak':
            self.oidc_client = KeycloakDiffgramClient()

    def get_client(self):
        return self.oidc_client
