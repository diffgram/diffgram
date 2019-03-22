import settings
from diffgram import Diffgram

project = Diffgram(
			client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID)

image_packet = {'media' : {
					'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					'type' : 'image'
					}
				}

# Single
project.file.from_packet(image_packet)


# Multiple
packet_list = [image_packet, image_packet, image_packet]

for packet in packet_list:
	project.file.from_packet(packet)

