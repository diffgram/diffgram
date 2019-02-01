

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
	directory_list = response.json()

	return directory_list


