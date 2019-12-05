from diffgram import Project

project = Project(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

url = "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg"

result = project.file.from_url(url)

print(result)