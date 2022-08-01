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


def set_jwt_in_session(token_data: dict):
    """
        Sets the JWT data in the client cookie session.
    :param token_data:
    :return:
    """

    oidc = OAuth2Provider()
    oidc_client = oidc.get_client()
    refresh_token = oidc_client.get_refresh_token_from_jwt(jwt_data = token_data)
    str_comp = zlib.compress(refresh_token.encode())
    login_session['jwt'] = str_comp


def get_decoded_jwt_from_session() -> str or None:
    """
        Gets the JWT from the client cookie.
    :return: String representing the refresh token
    """

    jwt_refresh_token = login_session.get('jwt')
    if type(jwt_refresh_token) == str:
        return jwt_refresh_token
    if jwt_refresh_token is None:
        return None
    refresh_token_string = zlib.decompress(jwt_refresh_token).decode()
    return refresh_token_string


def LoggedIn():
    if settings.USE_OAUTH2:
        oidc = OAuth2Provider()
        oidc_client = oidc.get_client()
        refresh_token = get_decoded_jwt_from_session()
        if refresh_token is None:
            return False

        try:
            new_token = oidc_client.refresh_token(refresh_token)
            if not new_token:
                return False
            new_refresh_token = oidc_client.get_refresh_token_from_jwt(jwt_data = new_token)
            if new_refresh_token is not None:
                login_session['jwt'] = new_refresh_token
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
    refresh_token = get_decoded_jwt_from_session()
    if refresh_token is None:
        return None
    access_token_data = oauth2_client.refresh_token(token = refresh_token)
    access_token = oauth2_client.get_access_token_from_jwt(jwt_data = access_token_data)
    if access_token_data is None:
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


def get_session_string():
    if settings.USE_OAUTH2:
        oauth2 = OAuth2Provider()
        oauth2_client = oauth2.get_client()
        rf_token = get_decoded_jwt_from_session()
        access_token_data = oauth2_client.refresh_token(token = rf_token)
        access_token = oauth2_client.get_access_token_from_jwt(jwt_data = access_token_data)
        return access_token
    else:
        return login_session.get('user_id')


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
