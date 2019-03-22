import warnings


def label_new(self, 
			  label,
			  allow_duplicates=False,
			  print_success=True):
	"""

	Arguments
		self,
		label_list, a list of label strings
		ignore_duplicates, bool
		print_success, bool
		
	Expects

	Returns

	"""

	# Check if already exists
	name = label.get('name', None)
	if not name:
		raise Exception("Please provide a key of name with a value of label")

	if allow_duplicates is False:

		label_file_id = self.name_to_file_id.get(name, None)

		if label_file_id:
			warnings.warn("\n\n '" + name + "' label already exists and was skipped." + \
				"\n Set allow_duplicates = True to bypass this check. \n")
			return

	endpoint = "/api/v1/project/" + self.project_string_id + \
			   "/label/new"

	response = self.session.post(self.host + endpoint,
								 json = label)

	data = response.json()

	if data["log"]["success"] == True:
		if print_success is True:
			print("New label success")
	else:
		raise Exception(data["log"]["errors"])