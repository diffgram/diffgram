from methods.regular.regular_api import *
from flask import redirect
import uuid
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from methods.user.login import first_stage_login_success
from methods.user.account.account_new import user_new_core, set_password_and_login_history
def login_and_return_access_token(session, diffgram_user, user_data, access_token_data, log):
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
        email = user_data.get('email')
        diffgram_user = User.get_user_by_oidc_id(session = session,
                                                 oidc_id = user_id)
        if diffgram_user:
            return login_and_return_access_token(
                session = session,
                diffgram_user = diffgram_user,
                user_data = user_data,
                access_token_data = access_token_data,
                log = log
            )
        # Check if user exists from email
        diffgram_user = User.get_by_email(session=session, email = email)
        if diffgram_user:
            diffgram_user.bind_to_oidc_login(session = session, oidc_id = user_id)
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
        # Case of a new user
        logger.info(f'Creating new user from OIDC Login ID {user_id}')
        new_user, log = user_new_core(session = session, email = email, log = log)
        new_user.bind_to_oidc_login(session = session, oidc_id = user_id)
        if regular_log.log_has_error(log = log):
            return jsonify(log = log), 400
        # We'll use a random password here, since password will not be managed by diffgram in this case
        set_password_and_login_history(session = session,
                                       new_user = new_user,
                                       password = str(uuid.uuid4()),
                                       token_data = access_token_data)
        return jsonify({
            'access_token_data': access_token_data,
            'user_data_oidc': user_data,
            'new_user_created': True,
            'log': log,
            'user': new_user.serialize()
        })