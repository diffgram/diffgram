
try:
	from methods.regular.regular_api import *
except:
	from default.methods.regular.regular_api import *


# TODO this is old method?
# Uses project.directory_default project for dir

@routes.route('/api/project/<string:project_string_id>/file/remove', 
			  methods=['POST'])
@Project_permissions.user_has_project(["admin", "Editor"])
def remove_file(project_string_id):
	with sessionMaker.session_scope() as session:

		# Same method for multiple types of files

		data = request.get_json(force=True)   # Force = true if not set as application/json' 
		file = data.get('file', None)
		if file is None:
			return json.dumps("file is None"), 400, {'ContentType':'application/json'}

		file_id = file.get('id', None)
		if file_id is None:
			return json.dumps("id is None"), 400, {'ContentType':'application/json'}

		existing_file = session.query(File).filter(File.id == file_id).first()

		project = Project.get(session, project_string_id)
		user_requesting = session.query(User).filter(User.id == getUserID()).one()

		working_dir = project.directory_default

		
		remove_core(session, working_dir, existing_file)



		# Flush /  remove files from working dir?
		out = {'success' : True}
		return jsonify(out), 200, {'ContentType':'application/json'}

		# file was previously committed so we need to copy it
		# A user may make changes to a file (resulting in a new file)
		# But that new file may not be committed
		# it will still have a parent_id which is why we have parent_id condition


def archive_related_tasks(session, file):
	"""
		Give a file, archive all the related tasks. This is used in the
		context of a cascade delete where the user deletes a file and
		wants to delete all the related tasks of that file.
	:param session:
	:param file:
	:return:
	"""
	tasks = session.query(Task).filter(
		Task.file_id == file.id
	).update({
		'status': 'archived'
	})
	return tasks


## Let's just move this into File class ??

def remove_core(session, working_dir, existing_file, cascade_archive_tasks = False):
	# Careful this needs to be first
	# since we return on ohter condition ... could be better

	if existing_file.parent_id or existing_file.committed is True:

		# Why we are making a new file here is not 
		# very clear, but since we are I think we need 
		# to remove the existing link
		 
		new_file = File.copy_file_from_existing(
			session, 
			working_dir, 
			existing_file,
			remove_link = True,	 
			add_link = False)
		
		new_file.state = "removed"
		new_file.hash_update()
		if cascade_archive_tasks:
			archive_related_tasks(session, existing_file)
		session.add(new_file)


		return True

	if existing_file.parent_id is None:

		existing_file.state = "removed"

		if cascade_archive_tasks:
			archive_related_tasks(session, existing_file)
		session.add(existing_file)
		return True
