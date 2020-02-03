from diffgram.file.file import File



def get_directory_list(self):
	"""
	Get a list of available directories for a project

	Arguments
		self
		
	Expects
		self.project_string_id

	Returns
		directory_list, array of dicts
		
	"""

	if self.project_string_id is None:
		raise Exception("No project string." + \
						"Set a project string using .auth()")

	if type(self.project_string_id) != str:
		raise Exception("project_string_id must be of type String")

	endpoint = "/api/v1/project/" + self.project_string_id + \
			   "/directory/list"

	response = self.session.get(self.host + endpoint)

	self.handle_errors(response)

	directory_list = response.json()

	return directory_list


def set_directory_by_name(self, name):
	"""

	Arguments
		self
		name, string		
		
	"""

	if name is None:
		raise Exception("No name provided.")

	# Don't refresh by default, just set from existing

	names_attempted = []
	did_set = False

	for directory in self.directory_list:

		nickname = directory.get("nickname")
		if nickname == name:
			self.set_default_directory(directory.get("id"))
			did_set = True
			break
		else:
			names_attempted.append(nickname)
		
	if did_set is False:
		raise Exception(name, " does not exist. Valid names are: " + 
				  str(names_attempted))


class Directory():

	def __init__(self,
			     client):

		self.client = client


	def new(self, name: str):
		"""
		Create a new directory and update directory list.

		We include name in exception message since this may
		be included in larger functions in which
		the name may be unclear

		"""
		if name is None:
			raise Exception("No name provided.")

		# Confirm not in existing
		# generator expression returns True if the directory
		# is not found. this is a bit awkward.
		if next((dir for dir in self.client.directory_list
				  if dir['nickname'] == name), True) is not True:
			raise Exception(name, "Already exists")

		packet = {'nickname' : name}

		endpoint = "/api/v1/project/" + \
			self.client.project_string_id + "/directory/new"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = packet)

		self.client.handle_errors(response)
		
		data = response.json()

		project = data.get('project')
		if project:
			directory_list = project.get('directory_list')
			if directory_list:
				self.client.directory_list = directory_list


	def list_files(
			self, 
			limit=None):
		"""
		Get a list of files in directory (from Diffgram service). 
	
		Assumes we are using the default directory.
		this can be changed ie by: 	project.set_directory_by_name(dir_name)
		
		We don't have a strong Directory concept in the SDK yet 
		So for now assume that we need to 
		call 	project.set_directory_by_name(dir_name)   first
		if we want to change the directory


		WIP Feb 3, 2020
			A lot of "hard coded" options here.
			Want to think a bit more about what we want to
			expose options here and what good contexts are.

		"""

		directory_id = self.client.directory_id
		#print("directory_id", directory_id)

		metadata = {'metadata' :
			{
				'directory_id': directory_id,
				'annotations_are_machine_made_setting': "All",
				'annotation_status': "All",
				'limit': limit,
				'media_type': "All",
				'request_next_page': False,
				'request_previous_page': False,
				'file_view_mode': "annotation"
			}
		}

		# User concept, in this context, is deprecated
		# 'sdk' is a placeholder value

		endpoint = "/api/project/" + \
			self.client.project_string_id + \
			"/user/sdk" + "/file/list"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = metadata)

		self.client.handle_errors(response)
		
		# Success
		data = response.json()
		file_list_json = data.get('file_list')

		# TODO would like this to perhaps be a seperate function
		# ie part of File_Constructor perhaps
		file_list = []
		for file_json in file_list_json:
			file = File.new(file_json = file_json)
			file_list.append(file)

		return file_list




