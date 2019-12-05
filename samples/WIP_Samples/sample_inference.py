import settings
from diffgram.core.core import Project
from diffgram.models import get_model


client = Project()

client.auth(client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID)

image_packet = {'media' : {
					'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					'type' : 'image'
					}
				}

file = image.from_url()

# Public example

client.auth(project_string_id = "imagenet")


# Uses latest (deployed?) model in project by default
# If no thing is available spins up new one
# Stores inferences by default
# By default renders info onto image it saves...

inference = client.predict(packet = image_packet)



# Choose network

inference = client.predict(packet = image_packet,
						   network = "named_network")



client.auth(project_string_id = "imagenet")
network = client.get_model()	# gets default

# / infers it's a project
# if not / trys from project

# state in client vs network object
# other stuff in client that's not prediction

project_a = Project()

# client maybe call project

named_model = project_a.get_model()	# default

named_model = project_a.get_model(network = "named_model")

# Seperate
file = diffgram.url(url)
inference = network.predict(file)

# Chained
network.predict(packet = image_packet)

network.predict(packet = "file_id or file_hash")

detector = diffgram_get_model(network = "imagenet/detector")
# This calles client.auth() for imagenet
# named_mode == detector  in terms of class object

# string of projects vs model()

detector.predict(packet = image_packet)

# model set object, calls sub models and returns dict,
# better using existing than client.predict(list)

class Image

@classmethod
def from_file(cls, file_path):
   blah

# how do we get the file hash
# file_list = diffgram.file_list(filter by all completed)
@classmethod
def from_diffgram_hash(cls, hash):
   blah

@classmethod
def from_url(cls, url):
   blah

def b64_encode(self):
    returns b64 encoded

inside client.predict(blah, blah, image_object):
   as_b64 = image_object.b64_encode()
   do whatever with as_b64


# Run three networks on same image

inference = client.predict(packet = image_packet,
						   networks = ["named_network", "abc", "xyz"])



print(inference.status or inference.result)

# View processed image
inference.view()

print(inference.boxes)

# Return location of (class?) in bounding box cordinates
print(inference.location)

# Other network stuff...

# Feed network somewhere and do something etc...

if inference.something > .50:

	# send email
	client.email_me()


# View Project file link
inference.diffgram_link



inference = client.predict(packet = image_packet,
						   network = "named_network")


action_map = {
	"class_a" : "action_y",
	"class_b" : "send_to_ocr"
	}

client.map(action_map)

# ie predicts accross 10 classes
# if class x is detected, sends to next process


