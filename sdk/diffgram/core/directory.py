

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
		raise Exception("Name does not exist, valid names are: " + 
				  str(names_attempted))



