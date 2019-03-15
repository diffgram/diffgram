
from diffgram.core.core import Diffgram
import settings

client = Diffgram()

client.auth(client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID)

brain = client.get_model()		# Gets default if no named provided

url = "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg"

inference = brain.predict_from_url(url)

