

def convert_label(self, instance, name):

	instance["label_file_id"] = self.client.name_to_file_id.get(name, None)

	if not instance["label_file_id"]:
		raise Exception(" \n '" + name + "' label is not in your project. \n " + \
			"See sample_new_labels.py for how to create a label, or create one on Diffgram.com" )

	return instance


