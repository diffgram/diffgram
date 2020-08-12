
def add_to_dir(project):

	name = "apples"
	apples_directory = project.directory.get(name)

	print(apples_directory.nickname)
	assert apples_directory.nickname == name

	file_id_list = [1025104, 1025103]

	result = apples_directory.add(file_id_list = file_id_list)

	print(result)