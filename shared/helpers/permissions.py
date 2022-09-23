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
import bz2
import gzip

logger = get_shared_logger()


def set_jwt_in_session(token_data: dict):
    """
        Sets the JWT data in the client cookie session.
    :param token_data:
    :return:
    """

    oidc = OAuth2Provider()
    oidc_client = oidc.get_client()

    id_token = oidc_client.get_id_token_from_jwt(jwt_data = token_data)
    refresh_token = oidc_client.get_refresh_token_from_jwt(jwt_data = token_data)
    access_token = oidc_client.get_access_token_from_jwt(jwt_data = token_data)

    str_id_comp = gzip.compress(id_token.encode())
    str_refresh_comp = gzip.compress(refresh_token.encode())
    str_access_comp = gzip.compress(access_token.encode())

    logger.info(f'ID Token Original size: {sys.getsizeof(id_token)} - Compressed Size: {sys.getsizeof(str_id_comp)}')
    logger.info(
        f'Access_token Token Original size: {sys.getsizeof(access_token)} - Compressed Size: {sys.getsizeof(str_access_comp)}')
    logger.info(
        f'Refresh Token Original size: {sys.getsizeof(refresh_token)} - Compressed Size: {sys.getsizeof(str_refresh_comp)}')

    login_session.clear()
    login_session['refresh_token'] = str_refresh_comp
    login_session['access_token'] = str_access_comp
    login_session['id_token'] = str_id_comp


def get_decoded_refresh_token_from_session() -> str or None:
    """
        Gets the JWT from the client cookie.
    :return: String representing the refresh token
    """

    jwt_token = login_session.get('refresh_token')
    if type(jwt_token) == str:
        return jwt_token
    if jwt_token is None:
        return None
    token_string = gzip.decompress(jwt_token).decode()
    return token_string


def get_decoded_id_token_from_session() -> str or None:
    """
        Gets the JWT from the client cookie.
    :return: String representing the ID token
    """
    oidc = OAuth2Provider()
    oidc_client = oidc.get_client()
    id_token = login_session.get('id_token')
    if type(id_token) == str:
        return id_token
    if id_token is None:
        return None
    token_string = gzip.decompress(id_token).decode()
    expired = oidc_client.id_token_has_expired(id_token = token_string)
    if expired:
        token_string = try_refreshing_tokens()

    return token_string


def get_decoded_access_token_from_session() -> str or None:
    """
        Gets the JWT from the client cookie.
    :return: String representing the ID token
    """
    oidc = OAuth2Provider()
    oidc_client = oidc.get_client()
    access_token = login_session.get('access_token')
    if type(access_token) == str:
        return access_token
    if access_token is None:
        return None
    token_string = gzip.decompress(access_token).decode()
    expired = oidc_client.id_token_has_expired(id_token = token_string)
    if expired:
        token_string = try_refreshing_tokens()

    return token_string


def try_refreshing_tokens() -> str or None:
    try:
        oidc = OAuth2Provider()
        oidc_client = oidc.get_client()
        refresh_token = get_decoded_refresh_token_from_session()
        new_token = oidc_client.refresh_token(refresh_token)
        new_refresh_token = oidc_client.get_refresh_token_from_jwt(jwt_data = new_token)
        new_id_token = oidc_client.get_id_token_from_jwt(jwt_data = new_token)
        new_access_token = oidc_client.get_access_token_from_jwt(jwt_data = new_token)
        if new_refresh_token is not None:
            login_session['refresh_token'] = new_refresh_token
        # if new_id_token is not None:
        #     login_session['id_token'] = new_id_token
        if new_access_token is not None:
            login_session['access_token'] = new_access_token
        return new_access_token
    except:
        msg = traceback.format_exc()
        logger.warning(f'Refresh token failed {msg}')
        return None


def LoggedIn():
    if settings.USE_OAUTH2:
        try:
            # id_token = get_decoded_id_token_from_session()
            access_token = get_decoded_access_token_from_session()
            if not access_token:
                return False
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
    access_token = get_decoded_access_token_from_session()
    if access_token is None:
        return None
    decoded_token = oauth2_client.get_decoded_jwt_token(id_token = access_token)
    if not decoded_token:
        return None
    diffgram_user = User.get_user_by_oauth2_id(session = session,
                                               oidc_id = decoded_token.get('sub'))
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
        # New Approach (ID TOKEN)
        token = get_decoded_id_token_from_session()
        # oauth2 = OAuth2Provider()
        # oauth2_client = oauth2.get_client()

        # access_token_data = oauth2_client.refresh_token(token = token)
        # access_token = oauth2_client.get_access_token_from_jwt(jwt_data = access_token_data)
        return token
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
