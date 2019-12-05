from diffgram import Project

project = Project(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

path = "file_path"

file = project.file.from_local(path)

print(file.id)