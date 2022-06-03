# OPENCORE - ADD
import traceback
from flask import session as login_session
from flask import request, redirect, url_for, flash
from shared.helpers import sessionMaker
from shared.database import hashing_functions
import sys, os
from shared.auth.KeycloakDiffgramClient import KeycloakDiffgramClient
from shared.settings import settings

from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


# True means has permission, False means doesn't.

def LoggedIn():
    if settings.USE_OIDC:
        jwt = login_session.get('jwt')
        access_token = jwt.get('access_token')
        refresh_token = jwt.get('refresh_token')
        if jwt is None:
            return False
        kc_client = KeycloakDiffgramClient()
        try:
            user = kc_client.get_user(access_token)
            if not user:
                return False
            new_token = kc_client.refresh_token(refresh_token)
            login_session['jwt'] = new_token
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


def get_user_from_oidc(session):
    from shared.database.user import User
    kc_client = KeycloakDiffgramClient()
    jwt = login_session.get('jwt')
    if jwt is None:
        return None
    access_token = jwt.get('access_token')
    if access_token is None:
        return None
    oidc_user = kc_client.get_user(access_token = access_token)
    if not oidc_user:
        return None
    diffgram_user = User.get_user_by_oidc_id(session = session,
                                             oidc_id = oidc_user.get('sub'))
    if not diffgram_user:
        return None
    return diffgram_user.id


def getUserID(session):
    if settings.USE_OIDC:
        return get_user_from_oidc(session = session)
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
    login_session['jwt'] = token_data


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
