from methods.regular.regular_api import *

from shared.database.attribute.attribute_template_group import Attribute_Template_Group
from shared.database.attribute.attribute_template_group_to_file import Attribute_Template_Group_to_File


@routes.route('/api/v1/project/<string:project_string_id>' +
			  '/attribute/group/update', 
			  methods=['POST'])
@Project_permissions.user_has_project(
	Roles = ["admin", "Editor"],
	apis_user_list = ['api_enabled_builder', 'security_email_verified'])
@limiter.limit("20 per day")
def api_attribute_template_group_update(project_string_id):  
	"""
	

	"""

	spec_list = [ 
		{'group_id' : int},
		{'name' : None},
		{'prompt' : None},
		{'kind' : str},
		{'label_file_list' : None},
		{'default_value' : None},
		{'default_id' : None},
		{'min_value' : None},
		{'max_value' : None},
		{'mode' : str},
        {'is_global' : None}
		]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400
	
	with sessionMaker.session_scope() as session:

		user = User.get(session = session)
		project = Project.get(session, project_string_id)

		group = Attribute_Template_Group.get_by_id(
				session = session,
				id = input['group_id'],
				project_id = project.id)

		if group is None:
			log['error']['group'] = "No group found"
			return jsonify(log=log), 400

		log = group_update_core(
				session = session,
				project = project,
				group = group,
				name = input['name'],
				prompt = input['prompt'],
				label_file_list = input['label_file_list'],
				mode = input['mode'],
				kind = input['kind'],
				log = log,
				member = user.member,
				default_value = input['default_value'],
				min_value = input['min_value'],
				max_value = input['max_value'],
				default_id = input['default_id'],
                is_global = input['is_global'])

		if len(log["error"].keys()) >= 1:
			return jsonify(log=log), 400

		log['success'] = True
		return jsonify(
			group = group.serialize(),
			log=log), 200


def group_update_core(
		session,
		project,
		group,
		name,
		prompt,
		label_file_list,
		mode,
		kind: str,
		log,
		member,
		default_value = None,
		min_value = None,
		max_value = None,
		default_id: int = None,
        is_global: bool = False):


	if mode == "ARCHIVE":
		
		group.archived = True
		session.add(group)


		# delete existing attachements to labels
		# Note this does not delete instances with this group. 

		existing_attachement_list = Attribute_Template_Group_to_File.get_all_from_group(
				session = session,
				group_id = group.id)


		for attachement in existing_attachement_list:

			# Do we just delete the attachement then?
			# Would it be better to archive it?
			session.delete(attachement)


		return log


	if mode == "UPDATE":

		if label_file_list is not None:
			# Create Attribute_Template_Group_to_File for ones
			# That don't exist? 

			# We get existing first
			# If it exists we remove it from id list
			# at end we remove remaining ones

			# Another option woudl be just to delete all existing and then
			# recreate with new list provided, but in case there's an error
			# not a fan of that...

			existing_attachement_list = Attribute_Template_Group_to_File.get_all_from_group(
				session = session,
				group_id = group.id)

			file_id_list = [attachement.file_id for attachement in existing_attachement_list ]

			for label_file_untrusted in label_file_list:

				untrusted_label_file_id = label_file_untrusted.get('id')            

				if untrusted_label_file_id in file_id_list:
					file_id_list.remove(untrusted_label_file_id)
					continue

				label_file = File.get_by_id_untrusted(
					session = session, 
					user_id = None, 
					project_string_id = project.project_string_id, 
					file_id = untrusted_label_file_id)

				if label_file is None:
					log['error']['label_file_id'] = f"Invalid{str(untrusted_label_file_id)}"
					return log

				new_attachment = Attribute_Template_Group_to_File.set(
					session = session,
					group_id = group.id,
					file_id = untrusted_label_file_id)

				session.add(new_attachment)

            # Alternatively we could get from db based on id...

			# remove any ones not added 
			for file_id in file_id_list:
				for existing_attachement in existing_attachement_list:
					if existing_attachement.file_id == file_id:
						session.delete(existing_attachement)



		session.add(group)

		group.is_new = False

		group.name = name
		group.min_value = min_value
		group.max_value = max_value
		group.prompt = prompt
		group.member_updated = member
		group.kind = kind
		group.default_value = default_value
		group.default_id = default_id
		group.is_global = is_global
		
		log['info']['update'] = "Success"

		return log

