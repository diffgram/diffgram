import settings
from diffgram.core.core import Diffgram

diffgram = Diffgram()

diffgram.auth(client_id = settings.CLIENT_ID,
			  client_secret = settings.CLIENT_SECRET,
			  project_string_id = settings.PROJECT_STRING_ID)


# Single
apple = {'name' : 'apple'}

diffgram.label_new(apple)

# Multiple
oranges = {'name' : 'bears'}  
pears = {'name' : 'pears'}

label_list = [oranges, pears]

for label in label_list:
	diffgram.label_new(label)


