# OPENCORE - ADD
from shared.database.user import User
from flask import request
from shared.database.auth.api import Auth_api


def get_member(session):
	"""
	An issue of this being part of auth is that we may want the actual 
	member object available in the session,
	and at least our current process is to close / not pass the 
	session used in auth. That perhaps is a good area to change
	but either way core logic here is similar.
	"""
	member = None

	# Potential to be outside of request context
	if not request:
		return member

	user = User.get(session)
	if user:
		member = user.member
	else:
		client_id = request.authorization.get('username', None)
		auth = Auth_api.get(session, client_id)
		member = auth.member

	return member