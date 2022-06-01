from methods.regular.regular_api import *
from flask import redirect
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient

@routes.route('/api/v1/auth/oidc-callback', methods = ['GET'])
def api_oidc_callback():
    """
        OIDC Callback
    :return:
    """

    print('AAAA', request.args)
    code = request.args.get('code')

    with sessionMaker.session_scope() as session:
        keycloak = KeycloakDiffgramClient()
        access_token = keycloak.get_access_token_with_code_grant(code = code)
        print('ACCESS TOKEN', access_token)
        return redirect(f'{settings.URL_BASE}/user/login-oidc')
