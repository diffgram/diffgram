

def convert_label(self, instance, name):

	instance["label_file"] = {}
	instance["label_file"]["id"] = self.name_to_file_id[name]

	return instance


