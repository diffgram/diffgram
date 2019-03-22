import settings
from diffgram import Diffgram

project = Diffgram(
			client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID
			)

brain = project.get_model(name = "my model")

# Local
path = ""
inference = brain.predict_from_local(path)

# URL
url = ""
inference = brain.predict_from_url(url)

# Diffgram file
inference = brain.predict_from_file(file_id = 111546)

