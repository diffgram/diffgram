from keycloak import KeycloakOpenID
from keycloak.keycloak_admin import KeycloakAdmin

from shared.settings import settings
import jwt
from shared.shared_logger import get_shared_logger
import traceback

logger = get_shared_logger()

REDIRECT_URI_DIFFGRAM = f'{settings.URL_BASE}user/oidc-login'

DEFAULT_PROJECT_ROLES = [
    "admin",
    "viewer",
    "editor"
]

DEFAULT_GLOBAL_ROLES = [
    "normal_user",
    "super_admin",
]

class KeycloakDiffgramClient:
    keycloak: KeycloakOpenID

    def __init__(self):
        self.keycloak = KeycloakOpenID(server_url = settings.OIDC_PROVIDER_HOST,
                                       client_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = settings.OIDC_PROVIDER_SECRET)

    def setup_keycloak_diffgram_install(self):
        """
            Creates diffgram realm and client for diffgram install as well as the default diffgram
            client roles.
        :return:
        """
        # Create a new Realm
        keycloak_admin = KeycloakAdmin(server_url = settings.OIDC_PROVIDER_HOST,
                                       username = settings.KEY_CLOAK_USER,
                                       password = settings.KEY_CLOAK_PASSWORD,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = settings.OIDC_PROVIDER_SECRET,
                                       verify = True)
        keycloak_admin.create_realm(payload = {"realm": settings.OIDC_PROVIDER_REALM}, skip_exists = True)
        keycloak_admin.create_client(payload = {"realm-name": settings.OIDC_PROVIDER_REALM}, skip_exists = True)

        for role_name in DEFAULT_PROJECT_ROLES:
            keycloak_admin.create_client_role(client_role_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                              payload = {'name': 'roleName', 'clientRole': True})

    def refresh_token(self, token):
        return self.keycloak.refresh_token(refresh_token = token)

    def logout(self, refresh_token):
        self.keycloak.logout(refresh_token)

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
