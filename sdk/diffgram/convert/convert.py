

def convert_label(self, instance):
	"""
	We assume if a label_file_id exists it supersedes a conversion from string name.
	"""

	label_file_id = instance.get('label_file_id')
	if label_file_id:
		return

	name = instance.get('name')

	if not name:
		raise Exception("Key Error: Instance must have a key 'name'.")

	instance["label_file_id"] = self.client.name_to_file_id.get(name, None)

	if not instance["label_file_id"]:
		raise Exception(" \n '" + name + "' label is not in your project. \n " + \
			"See sample_new_labels.py for how to create a label, or create one on Diffgram.com" )

	return instance


