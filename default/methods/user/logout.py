from flask import session as login_session
from methods import routes
from shared.settings import settings
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.auth.OAuth2Provider import OAuth2Provider


def oauth2_logout() -> [dict, int]:
    oauth2 = OAuth2Provider()
    jwt_data = login_session.get('jwt')
    oauth_client = oauth2.get_client()
    refresh_token = oauth_client.get_refresh_token_from_jwt(jwt_data = jwt_data)
    login_session['jwt'] = None
    url_data = oauth_client.logout(refresh_token = refresh_token)
    return {"url_redirect": url_data}, 200


@routes.route('/api/v1/user/logout', methods = ['GET'])
def logout():
    if settings.USE_OAUTH2:
        return oauth2_logout()
    else:
        login_session['user_id'] = ''
        return {"url_redirect": None}, 200
