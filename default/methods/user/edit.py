# OPENCORE - ADD
from methods.regular.regular_api import *

from google.cloud import storage
import logging
import sys
import re
import json
import tempfile
import os
from werkzeug.utils import secure_filename

from shared.helpers.permissions import getUserID

from shared.database import hashing_functions
from shared.helpers.permissions import setSecureCookie
from shared.helpers.permissions import get_gcs_service_account

from shared.database.user import Signup_code

from methods.images.images_core import process_profile_image
from methods.images.images_core import process_image_generic


# Define error handling functions for user creation
# Allow a-z, A-Z, 0-0, _, - using regular expression
# 3 - 20 characters
#USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,50}$")

PASS_RE = re.compile(r"^.{3,50}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


NAME_RE = re.compile(r"^[a-zA-Z]{2,50}$")

def valid_name(name):
	return name and NAME_RE.match(name)

def valid_username(username):
	return username and USER_RE.match(username)

def valid_password(password):
	return password and PASS_RE.match(password)

def valid_email(email):
	return email and EMAIL_RE.match(email)


@routes.route('/api/user/edit', methods=['POST'])
@General_permissions.grant_permission_for(['normal_user', 'super_admin'])
def user_edit():  

	error_list = []

	with sessionMaker.session_scope() as session:

		data = request.get_json(force=True)   # Force = true if not set as application/json' 
		user = data.get('user', None)
		if user is None:
			out = jsonify(success = None,
						  error_list = ["No user"])
			return out, 400, {'ContentType':'application/json'}

		# May want to update users other than the requesting user...
		#db_user = session.query(User).filter_by(email=user['email']).first()

		# Permissions model here assumes that we know who the user is
		# So therefore can only update for self

		db_user = session.query(User).filter(User.id == getUserID()).one()

		# Update info
		# TODO lots of checks and things to consider here...

		db_user.first_name = user.get('first_name', None)
		db_user.last_name = user.get('last_name', None)

		session.add(db_user)

		out = jsonify(success = True,
					  errors = [],
					  user = db_user.serialize())
		return out, 200, {'ContentType':'application/json'}



images_allowed_file_names = [".jpg", ".jpeg", ".png"]


@routes.route('/api/user/upload/profile_image', methods=['POST'])
@General_permissions.grant_permission_for(['normal_user', 'super_admin'])
def user_upload_profile_image():

	file = request.files.get('file')
	if not file:
		return "No file", 400
		
	extension = os.path.splitext(file.filename)[1].lower()
	if extension in images_allowed_file_names:

		file.filename = secure_filename(file.filename) # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/          
		temp_dir = tempfile.mkdtemp()
		file_name = f"{temp_dir}/{file.filename}"
		file.save(file_name)

		with sessionMaker.session_scope() as session:
			
			with open(file_name, "rb") as file:              
				content_type = f"image/{str(extension)}"
				short_file_name = os.path.split(file_name)[1]

				user = session.query(User).filter(User.id == getUserID()).one()
					
				image = process_profile_image(
					session=session, user=user,
					file=file, file_name=short_file_name, 
					content_type=content_type, extension=extension)

			Event.new(
				kind = "profile_image_update",	
				session = session,
				member = user.member,
				success = True
				)
		
			return jsonify(success=True,
						   user=user.serialize()), 200, {'ContentType':'application/json'}


	return jsonify(success=False), 400, {'ContentType':'application/json'}


