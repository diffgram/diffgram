from flask import session as login_session
from methods import routes
from shared.settings import settings
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.auth.OAuth2Provider import OAuth2Provider
from shared.helpers.permissions import get_decoded_refresh_token_from_session


def oauth2_logout() -> [dict, int]:
    oauth2 = OAuth2Provider()
    refresh_token = get_decoded_refresh_token_from_session()
    oauth_client = oauth2.get_client()
    login_session['refresh_token'] = None
    login_session['id_token'] = None
    login_session.clear()
    # url_data = oauth_client.logout(refresh_token = refresh_token)
    return {"url_redirect": None}, 200


@routes.route('/api/v1/user/logout', methods = ['GET'])
def logout():
    if settings.USE_OAUTH2:
        return oauth2_logout()
    else:
        login_session['user_id'] = ''
        return {"url_redirect": None}, 200
