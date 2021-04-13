# OPENCORE - ADD
from methods.regular.regular_api import *

import re

from shared.database.attribute.attribute_template import Attribute_Template
from shared.database.attribute.attribute_template_group import Attribute_Template_Group


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/attribute', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor"],
	apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("200 per day")
def api_attribute_update_or_new(project_string_id):  
	"""
	Shared route for update and new

	"""

	spec_list = [ 
		{'attribute' : dict},
		{'mode' : str}]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400
	
	with sessionMaker.session_scope() as session:

		user = User.get(session = session)
		project = Project.get(session, project_string_id)

		# Caution, declaring as user.member for now.
		member = user.member

		attribute_session = Attribute_Session(
			session = session,
			member = member,
			project = project,
			log = log,
			attribute_dict = input['attribute'],
			mode = input['mode']
			)

		# For init errors
		if len(attribute_session.log["error"].keys()) >= 1:
			return jsonify(log=log), 400


		if attribute_session.mode in ["UPDATE", "ARCHIVE"]:

			attribute_session.update_or_archive_mode_init()

			if len(attribute_session.log["error"].keys()) >= 1:
				return jsonify(log=log), 400


		attribute_session.main()
			
		log = attribute_session.log
		if len(log["error"].keys()) >= 1:
			return jsonify(log=log), 400

		attribute_template = attribute_session.attribute_template
		log['success'] = True

		if attribute_session.mode == "NEW":
			
			# Just putting it here for now while
			# Figuring out how we are loading member
			# Probably could be in attribute_session()
			Event.new(			
				session = session,
				kind = "new_attribute",
				member = member,
				success = True,
				project_id = project.id,
				email = user.email
				)

		out = jsonify(  attribute_template = attribute_template.serialize(),
						log = log)
		return out, 200


class Attribute_Session():
	"""
	Holding class so we don't have to keep calling 
	session and project for each function
	"""

	def __init__(
			self,
			session,
			member,
			project,
			log,
			attribute_dict,
			mode
			):

		self.session = session
		self.member = member
		self.project = project
		self.mode = mode
		self.log = log

		# Key point, attribute_dict is the UNTRUSTED dictionary input
		# Where as attribute is class Attribute object in our system as it gets created
		self.attribute_dict = attribute_dict
		self.mode = mode
		####

		self.attribute_template = None

		self.group = None

		# FUNCTIONS
		self.verify_and_set_group_id()


	def update_or_archive_mode_init(self):
		
		self.attribute_template = Attribute_Template.get_by_id(
			session = self.session,
			id = self.attribute_dict.get('id'),
			project_id = self.project.id)

		if self.attribute_template is None:
			log['error']['attribute'] = "No attribute found"
			return

		# TODO check self.mode in allowed modes?

		# Default archive case
		if self.mode == 'ARCHIVE':

			self.session.add(self.attribute_template)
			self.attribute_template.archived = True



	def verify_and_set_group_id(self):
		"""
		"""

		group_id = self.attribute_dict.get('group_id', None)
		if group_id is None:
			self.log['error']['group_id'] = "Invalid group_id (None provided.)"
			return

		self.group = Attribute_Template_Group.get_by_id(
			session = self.session,
			id = group_id,
			project_id = self.project.id)

		if self.group is None:
			self.log['error']['group'] = "Invalid group (Does not match project or bad id)."
			return

		if self.group.is_new is True:
			self.session.add(self.group)
			self.group.is_new = False


	def main(self):

		if self.mode == "ARCHIVE":
			# Special main() specific logic if required
			# Return since don't want to do anything else here
			# This is kinda awkward
			return

		if self.mode == "NEW":
			self.new_attribute_template()

		if self.mode == "UPDATE":
			# Special logic for update if required.
			# pass since still want to use shared logic
			pass

		spec_list = [
			{'name': str}]

		self.log, input = regular_input.input_check_many(
			spec_list = spec_list,
			log = self.log,
			untrusted_input = self.attribute_dict)

		if len(self.log["error"].keys()) >= 1:
			return

		self.attribute_template.name = input['name']


		self.success()


	def success(self):
	
		self.session.add(self.attribute_template)
		self.session.flush()

		self.session.add(self.group)


	def new_attribute_template(self):
		"""

		"""

		self.attribute_template = Attribute_Template.new(
				project = self.project,
				member = self.member,
				group = self.group,
				)

