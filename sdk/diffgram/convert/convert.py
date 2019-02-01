

def convert_label(self, instance, name):

	instance["label_file"] = {}
	label_file_id = self.name_to_file_id.get(name, None)

	if not label_file_id:
		raise Exception(" \n '" + name + "' label is not in your project. \n " + \
			"See sample_new_labels.py for how to create a label, or create one on Diffgram.com" )

	instance["label_file"]["id"] = label_file_id

	return instance


