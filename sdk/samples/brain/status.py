import settings
from diffgram import Diffgram

project = Diffgram(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret")

brain = project.get_model(name = "my_model")

brain.check_status()

print(brain.status)
