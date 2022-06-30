try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient


@routes.route('/api/configs/is-oauth2-set')
def oidc_is_set():
    if settings.USE_OAUTH2 is False:
        return jsonify({"use_oauth2": False})

    is_set = settings.USE_OAUTH2 and \
             settings.OAUTH2_PROVIDER_HOST and \
             settings.KEYCLOAK_REALM and \
             settings.OAUTH2_PROVIDER_CLIENT_ID

    if is_set:
        kc_client = KeycloakDiffgramClient()
        login_url = kc_client.get_login_url()
        return jsonify({"use_oauth2": True, "login_url": login_url})
    return jsonify({"use_oauth2": False})
