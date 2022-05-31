from keycloak import KeycloakOpenID
from shared.settings import settings


class KeycloakDiffgramClient:
    keycloak: KeycloakOpenID

    def __init__(self):
        self.keycloak = KeycloakOpenID(server_url = settings.OIDC_PROVIDER_HOST,
                                       client_id = settings.OIDC_PROVIDER_CLIENT_ID,
                                       realm_name = settings.OIDC_PROVIDER_REALM,
                                       client_secret_key = settings.OIDC_PROVIDER_SECRET)
