import settings
from diffgram import Diffgram

project = Diffgram(
			client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID
			)

# Construct new training with all defaults

brain = project.train.start(method="object_detection",
						    name="my_model")

brain.check_status()

print(brain.status)
