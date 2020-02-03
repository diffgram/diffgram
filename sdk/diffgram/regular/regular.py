

def refresh_from_dict(
		instance,
		json_dict = None) -> None:
	"""
	instance is instance of a class

	Update object attributes in context of getting a serialized
	version of instance class from Diffgram Service.

	Usage example:
	
	file = File()
	refresh_from_dict(file, file_json)

	In general this is meant as an internal helper and not
	user exposed.
	
	"""

	if not json_dict:
		return

	if not isinstance(json_dict, dict):
		return

	for key, value in json_dict.items():
		setattr(instance, key, value)