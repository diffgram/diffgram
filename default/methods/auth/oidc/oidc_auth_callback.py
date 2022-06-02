from methods.regular.regular_api import *
from flask import redirect
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from methods.user.login import first_stage_login_success


@routes.route('/api/v1/auth/oidc-login', methods = ['POST'])
def api_oidc_callback():
    """
        OIDC Callback
    :return:
    """
    oidc_spec_list = [
        {"code": {
            'kind': str
        }},
    ]

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = oidc_spec_list)
    code = input.get('code')
    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        keycloak = KeycloakDiffgramClient()
        access_token_data = keycloak.get_access_token_with_code_grant(code = code)
        user_data = keycloak.get_user(access_token = access_token_data.get('access_token'))
        user_id = user_data.get('sub')
        diffgram_user = User.get_user_by_oidc_id(session = session,
                                                 oidc_id = user_id)
        if diffgram_user:
            first_stage_login_success(
                log = log,
                session = session,
                user = diffgram_user,
                jwt = access_token_data
            )

            return jsonify({
                'access_token_data': access_token_data,
                'user_data_oidc': user_data,
                'user': diffgram_user.serialize()
            })
