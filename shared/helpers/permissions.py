# OPENCORE - ADD
import traceback
from flask import session as login_session
from flask import request, redirect, url_for, flash
from shared.helpers import sessionMaker
from shared.database import hashing_functions
import sys, os
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.auth.OAuth2Provider import OAuth2Provider
from shared.settings import settings
import base64
from shared.shared_logger import get_shared_logger
import ast
import zlib

logger = get_shared_logger()


# True means has permission, False means doesn't.
def get_decoded_jwt_from_session() -> dict or None:
    jwt = login_session.get('jwt')
    if jwt is None:
        return None
    if type(jwt) == dict:
        return jwt
    jwt_string = zlib.decompress(jwt).decode()
    res = ast.literal_eval(jwt_string)
    return res


def LoggedIn():
    if settings.USE_OAUTH2:
        oidc = OAuth2Provider()
        oidc_client = oidc.get_client()
        jwt = get_decoded_jwt_from_session()
        access_token = oidc_client.get_access_token_from_jwt(jwt_data = jwt)
        refresh_token = oidc_client.get_refresh_token_from_jwt(jwt_data = jwt)
        if jwt is None:
            return False

        try:
            user = oidc_client.get_user(access_token)
            if not user:
                return False
            new_token = oidc_client.refresh_token(refresh_token)
            login_session['jwt'] = new_token
            login_session['jwt']['refresh_token'] = refresh_token
            return True
        except Exception as e:
            err_data = traceback.format_exc()
            logger.error(err_data)
            return False
    else:
        if login_session.get('user_id', None) is not None:
            out = hashing_functions.check_secure_val(login_session['user_id'])
            if out is not None:
                return True
            else:
                return False
        else:
            return False


def get_user_from_oauth2(session):
    from shared.database.user import User
    oauth2 = OAuth2Provider()
    oauth2_client = oauth2.get_client()
    jwt = get_decoded_jwt_from_session()
    if jwt is None:
        return None
    access_token = jwt.get('access_token')
    if access_token is None:
        return None
    oauth2_user = oauth2_client.get_user(access_token = access_token)
    if not oauth2_user:
        return None
    diffgram_user = User.get_user_by_oauth2_id(session = session,
                                               oidc_id = oauth2_user.get('sub'))
    if not diffgram_user:
        return None
    return diffgram_user.id


def getUserID(session):
    if settings.USE_OAUTH2:
        return get_user_from_oauth2(session = session)
    else:
        if login_session.get('user_id', None) is not None:
            out = hashing_functions.check_secure_val(login_session['user_id'])
            if out is not None:
                return out
    return None


def defaultRedirect():
    return redirect('/user/login')


def setSecureCookie(user_db):
    cookie_hash = hashing_functions.make_secure_val(user_db.id)
    login_session['user_id'] = cookie_hash


def set_jwt_in_session(token_data):
    token_str = str(token_data)
    str_comp = zlib.compress(token_str.encode())
    # message_bytes = token_str.encode('utf-8')
    # base64_bytes = base64.b64encode(message_bytes)
    # base64_string = base64_bytes.decode("ascii")
    login_session['jwt'] = str_comp


def get_current_version(session):
    user = session.query(User).filter_by(id = getUserID(session = session)).first()
    project = session.query(Project).filter_by(id = user.project_id_current).first()
    version = session.query(Version).filter_by(id = project.version_id_current).first()

    return version


def get_ml_settings(session, version):
    machine_learning_settings = session.query(Machine_learning_settings).filter_by(
        id = version.machine_learning_settings_id).first()
    return machine_learning_settings


def get_gcs_service_account(gcs):
    path = settings.SERVICE_ACCOUNT_FULL_PATH
    return gcs.from_service_account_json(path)
