# OPENCORE - ADD
from flask import session as login_session
from flask import redirect
from methods import routes
from shared.settings import settings
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.auth.OIDCProvider import OIDCProvider

oidc = OIDCProvider()

def oidc_logout():
    jwt_data = login_session.get('jwt')
    if jwt_data is None:
        login_session['jwt'] = ''
        return "Success", 200

    login_session['jwt'] = ''
    if type(jwt_data) == dict:
        access_token = jwt_data.get('access_token')
        refresh_token = jwt_data.get('refresh_token')
        kc_client = KeycloakDiffgramClient()
        kc_client.logout(refresh_token = refresh_token)


@routes.route('/api/v1/user/logout', methods = ['GET'])
def logout():
    if settings.USE_OIDC:
        oidc_logout()
    else:
        login_session['user_id'] = ''
    return "Success", 200
