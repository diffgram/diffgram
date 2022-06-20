from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient

class KeycloakPolicyEnforcer:

    def __init__(self):
        self.keycloak_client = KeycloakDiffgramClient()

