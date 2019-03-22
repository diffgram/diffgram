from diffgram import Diffgram

project = Diffgram(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

brain = project.get_model(name = "my model")

# Local
path = ""
inference = brain.predict_from_local(path)

# URL
url = ""
inference = brain.predict_from_url(url)

# Diffgram file
inference = brain.predict_from_file(file_id = 111546)

