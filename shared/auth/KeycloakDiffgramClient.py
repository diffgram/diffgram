from keycloak import KeycloakOpenID
from shared.settings import settings


class KeycloakDiffgramClient:
    keycloak: KeycloakOpenID

    def __init__(self):
        self.keycloak = KeycloakOpenID(server_url = settings.OIDC_PROVIDER_HOST,
                                       client_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = 'fPgFGua2uXUkYlvKRSIchOCEZly4Qld8')

    def get_access_token_with_code_grant(self, code):
        token = self.keycloak.token(grant_type = 'authorization_code',
                                    code = code,
                                    redirect_uri = f'{settings.URL_BASE}api/v1/auth/oidc-callback'
                                    )
        return token

    def get_user(self, access_token):
        user_data = self.keycloak.userinfo(token = access_token)
        return user_data