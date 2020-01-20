

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





