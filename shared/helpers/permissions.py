# OPENCORE - ADD
from flask import session as login_session
from flask import request, redirect, url_for, flash
from shared.helpers import sessionMaker
from shared.database import hashing_functions
import sys, os

from shared.settings import settings


# True means has permission, False means doesn't.

def LoggedIn():
	# TODO review this
	# Kind of silly to run the hash check just to check if they are logged in
	# Maybe rather just check if the 'user_id' cookie exists
	# Also concerned this may be confusing that you think you are checking a permission
	# When really just testing if the cookie exists

	if login_session.get('user_id', None) is not None:
		out = hashing_functions.check_secure_val(login_session['user_id'])
		if out is not None:
			return True
		else:
			return False
	else:
		return False

# Maybe this should be in User class?
def getUserID():
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

def get_current_version(session):
	user = session.query(User).filter_by(id=getUserID()).first()
	project = session.query(Project).filter_by(id=user.project_id_current).first()
	version = session.query(Version).filter_by(id=project.version_id_current).first()

	return version


def get_ml_settings(session, version):

	machine_learning_settings = session.query(Machine_learning_settings).filter_by(id=version.machine_learning_settings_id).first()
	return machine_learning_settings


def get_gcs_service_account(gcs):
	path = settings.SERVICE_ACCOUNT_FULL_PATH
	return gcs.from_service_account_json(path)


