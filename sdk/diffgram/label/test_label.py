

def test_sdk_get_label(project):
	"""
	"""

	# Labels that does not exist
	file = project.get_label(None)
	assert file is None

	file = project.get_label("apple")
	assert file is None

	# Files that do exist
	name_list = ["cat", "test", "third"]
	file_list = project.get_label(name_list=name_list)
	assert len(name_list) == len(file_list)

test_sdk_get_label()