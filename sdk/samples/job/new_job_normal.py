from diffgram import Project

"""
Normal job creation
"""

project = Project(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

directory_path = "../images_test/*"
path_list = glob.glob(directory_path)

file_list = []

for path in path_list:

	file = project.file.from_local(path)
	file_list.append(file)

guide = project.guide.new(
			name = "Traffic lights",
			description_markdown = "my description"
			)
	
job = project.job.new(
		name = "my job",
		instance_type = "box",
		share = "Project",
		file_list = file_list,
		guide = guide,
		launch = True
		)


