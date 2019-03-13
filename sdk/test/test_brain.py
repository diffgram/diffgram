
from diffgram.core.core import Diffgram
import settings_debug as settings

client = Diffgram(debug=True)

client.auth(client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID)




file = client.file.from_url(1, 1)

print(file)

#file2 = client.file.from_url(1, 1)

#print(file2)

file.id = 17

brain = client.get_model()

brain.predict(file)

