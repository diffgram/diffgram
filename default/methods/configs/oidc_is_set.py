try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient


@routes.route('/api/configs/is-oidc-set')
def oidc_is_set():
    if settings.USE_OIDC is False:
        return jsonify({"use_oidc": False})

    is_set = settings.USE_OIDC and \
             settings.OIDC_PROVIDER_HOST and \
             settings.OIDC_PROVIDER_REALM and \
             settings.OIDC_PROVIDER_CLIENT_ID

    if is_set:
        kc_client = KeycloakDiffgramClient()
        login_url = kc_client.get_login_url()
        return jsonify({"use_oidc": True, "login_url": login_url})
    return jsonify({"use_oidc": False})
