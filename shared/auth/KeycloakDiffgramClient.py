from keycloak import KeycloakOpenID
from shared.settings import settings
import jwt
from shared.shared_logger import get_shared_logger
import traceback

logger = get_shared_logger()

REDIRECT_URI_DIFFGRAM = f'{settings.URL_BASE}user/oidc-login'


class KeycloakDiffgramClient:
    keycloak: KeycloakOpenID

    def __init__(self):
        self.keycloak = KeycloakOpenID(server_url = settings.OIDC_PROVIDER_HOST,
                                       client_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = 'fPgFGua2uXUkYlvKRSIchOCEZly4Qld8')

    def get_login_url(self):
        return self.keycloak.auth_url(redirect_uri = REDIRECT_URI_DIFFGRAM)

    def get_access_token_with_code_grant(self, code):

        token = self.keycloak.token(grant_type = 'authorization_code',
                                    code = code,
                                    redirect_uri = REDIRECT_URI_DIFFGRAM
                                    )

        return token

    def get_user(self, access_token):
        user_data = self.keycloak.userinfo(token = access_token)
        return user_data

    def verify_jwt(self, access_token):
        """
        Verify that the JWT (access_token) can be decoded using the related client_id and public_key.
        :param access_token:
        :return: True or False
        """
        try:
            # Build the key in format accepted by JWT (python implementation)
            header = "-----BEGIN PUBLIC KEY-----\n"
            trailer = "\n-----END PUBLIC KEY-----"
            key = header + str(settings.OIDC_PROVIDER_PUBLIC_KEY).encode('utf-8') + trailer
            # Decode the token by using the server public key
            decoded = jwt.decode(access_token,
                                 key = key,
                                 algorithms = ['RS256'],
                                 audience = self.protected_client_id)
            return True, decoded
        except Exception as e:
            err = traceback.format_exc()
            logger.error(err)
            return False, e
