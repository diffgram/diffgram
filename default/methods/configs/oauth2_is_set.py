try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.auth.OAuth2Provider import OAuth2Provider


@routes.route('/api/configs/is-oauth2-set')
def oauth2_is_set():
    print('USE_OAUTH2', settings.USE_OAUTH2)
    print('OAUTH2_PROVIDER_HOST', settings.OAUTH2_PROVIDER_HOST)
    print('OAUTH2_PROVIDER_CLIENT_ID', settings.OAUTH2_PROVIDER_CLIENT_ID)
    if settings.USE_OAUTH2 is False:
        return jsonify({"use_oauth2": False})

    is_set = settings.USE_OAUTH2 and \
             settings.OAUTH2_PROVIDER_HOST and \
             settings.OAUTH2_PROVIDER_CLIENT_ID

    if is_set:
        oauth2 = OAuth2Provider()
        oauth2_client = oauth2.get_client()
        login_url = oauth2_client.get_login_url()
        return jsonify({"use_oauth2": True, "login_url": login_url})
    return jsonify({"use_oauth2": False})
