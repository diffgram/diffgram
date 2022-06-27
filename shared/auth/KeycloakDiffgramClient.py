from keycloak import KeycloakOpenID
from keycloak.keycloak_admin import KeycloakAdmin
from enum import Enum
from shared.settings import settings
import jwt
from shared.shared_logger import get_shared_logger
import traceback
from shared.utils.singleton import Singleton
from shared.auth.OIDCProvider import OIDCClientBase
logger = get_shared_logger()

REDIRECT_URI_DIFFGRAM = f'{settings.URL_BASE}user/oidc-login'




class DefaultProjectRoles(Enum):
    admin = 'admin'
    viewer = 'viewer'
    editor = 'editor'


class DefaultGlobalRoles(Enum):
    normal_user = 'normal_user'
    super_admin = 'super_admin'


class KeycloakDiffgramClient(OIDCClientBase):
    keycloak: KeycloakOpenID
    installed: bool
    client_secret: str

    def __init__(self):
        self.setup_keycloak_diffgram_install()
        self.keycloak = KeycloakOpenID(server_url = settings.OIDC_PROVIDER_HOST,
                                       client_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = self.client_secret)

    def setup_keycloak_diffgram_install(self):
        """
            Creates diffgram realm and client for diffgram install as well as the default diffgram
            client roles. This is function is used at startup to check that keycloak has all the data
            for diffgram to work correctly with it.
        :return:
        """
        self.keycloak_admin_master = KeycloakAdmin(server_url = settings.OIDC_PROVIDER_HOST,
                                                   username = settings.KEY_CLOAK_MASTER_USER,
                                                   password = settings.KEY_CLOAK_MASTER_PASSWORD)
        # Create a new Realm
        self.__create_diffgram_default_realm()

        # Create diffgram realm user
        user_id = self.__create_admin_user()

        # Create diffgram keycloak client.
        client_id = self.__create_default_diffgram_client()
        self.__get_client_secret()

        self.__setup_scopes_and_mappers()
        # Create default roles
        global_roles = self.__create_default_global_roles(client_id = client_id)
        logger.info(f'Added global roles: {global_roles}')

        # keycloak_admin.add_composite_client_roles_to_role()
        normal_user_role_name = DefaultGlobalRoles.normal_user.value
        project_roles = self.__create_default_project_roles(normal_user_role = normal_user_role_name,
                                                            client_id = client_id)
        logger.info(f'Added project roles: {project_roles}')

    def __setup_scopes_and_mappers(self):
        scopes = self.keycloak_admin_master.get_client_scopes()
        for s in scopes:
            if s.get('name') and s.get('name') in ['roles']:
                self.keycloak_admin_master.update_client_scope(client_scope_id = s.get('id'),
                                                               payload = {'attributes': {
                                                                   'display.on.consent.screen': True,
                                                                   'include.in.token.scope': True
                                                               }})
        # self.keycloak_admin_master.get_client_scope()

        return self.client_secret

    def __get_client_secret(self):
        client = self.keycloak_admin_master.get_client(settings.OIDC_PROVIDER_CLIENT_ID)
        secret = self.keycloak_admin_master.get_client_secrets(client_id = client.get('id'))
        self.client_secret = secret.get('value')
        return self.client_secret

    def __create_diffgram_default_realm(self) -> str:
        realm_id = self.keycloak_admin_master.create_realm(
            payload = {"realm": settings.OIDC_PROVIDER_REALM, 'enabled': True},
            skip_exists = True)
        return realm_id

    def __create_admin_user(self) -> str:

        self.keycloak_admin_master.realm_name = settings.OIDC_PROVIDER_REALM
        user_id = self.keycloak_admin_master.create_user(payload = {
            'username': settings.KEY_CLOAK_DIFFGRAM_USER,
            'enabled': True,
        },
            exist_ok = True)
        logger.info(f'Fetched Keycloak Admin User {user_id}')
        self.keycloak_admin_master.set_user_password(user_id = user_id,
                                                     password = settings.KEY_CLOAK_DIFFGRAM_PASSWORD,
                                                     temporary = False)
        return user_id

    def __create_default_diffgram_client(self) -> str:
        logger.info(f'Creating client {settings.OIDC_PROVIDER_CLIENT_ID}')
        client_id = self.keycloak_admin_master.create_client(
            payload = {'name': settings.OIDC_PROVIDER_CLIENT_ID,
                       'id': settings.OIDC_PROVIDER_CLIENT_ID},
            skip_exists = True)
        self.keycloak_admin_master.update_client(client_id,
                                                 {'authorizationServicesEnabled': True,
                                                  'serviceAccountsEnabled': True,
                                                  'redirectUris': [REDIRECT_URI_DIFFGRAM],
                                                  })
        logger.info(f'Fetched Keycloak Client for Diffgram:  {client_id}')
        return client_id

    def __create_default_global_roles(self, client_id: str) -> list:
        created_role_ids = []
        for enum_item in DefaultGlobalRoles:
            res = self.keycloak_admin_master.create_client_role(client_role_id = client_id,
                                                                payload = {'name': enum_item.value,
                                                                           'clientRole': True},
                                                                skip_exists = True)
            created_role_ids.append(res)
        return created_role_ids

    def __create_default_project_roles(self, normal_user_role: str, client_id: str) -> list:
        created_role_ids = []
        role = self.keycloak_admin_master.get_client_role(
            client_id = client_id,
            role_name = normal_user_role
        )
        for enum_item in DefaultProjectRoles:
            res = self.keycloak_admin_master.create_client_role(client_role_id = client_id,
                                                                payload = {'name': enum_item.value,
                                                                           'clientRole': True},
                                                                skip_exists = True)
            created_role = self.keycloak_admin_master.get_client_role(
                client_id = client_id,
                role_name = enum_item.value
            )
            res = self.keycloak_admin_master.add_composite_client_roles_to_role(client_role_id = client_id,
                                                                                role_name = enum_item.value,
                                                                                roles = [{'name': normal_user_role,
                                                                                          "id": role.get('id')}])
            created_role_ids.append(enum_item.value)
        return created_role_ids

    def refresh_token(self, token: str) -> dict:
        return self.keycloak.refresh_token(refresh_token = token)

    def logout(self, refresh_token: str):
        self.keycloak.logout(refresh_token)

    def get_login_url(self):
        return self.keycloak.auth_url(redirect_uri = REDIRECT_URI_DIFFGRAM)

    def get_access_token_with_code_grant(self, code: str) -> dict:

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

    def get_access_token_from_jwt(self, jwt_data: dict) -> str:

        return jwt_data.get('access_token')

    def get_refresh_token_from_jwt(self, jwt_data: dict) -> str:

        return jwt_data.get('refresh_token')
