from flask import session as login_session
from methods import routes
from shared.settings import settings
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.auth.OAuth2Provider import OAuth2Provider



def oidc_logout():
    oauth2 = OAuth2Provider()
    jwt_data = login_session.get('jwt')
    if jwt_data is None:
        login_session['jwt'] = ''
        return "Success", 200

    login_session['jwt'] = ''
    if type(jwt_data) == dict:
        refresh_token = jwt_data.get('refresh_token')
        oauth_client = oauth2.get_client()
        oauth_client.logout(refresh_token = refresh_token)


@routes.route('/api/v1/user/logout', methods = ['GET'])
def logout():
    if settings.USE_OAUTH2:
        oidc_logout()
    else:
        login_session['user_id'] = ''
    return "Success", 200
