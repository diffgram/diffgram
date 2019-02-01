import settings
from diffgram.core.core import Diffgram

diffgram = Diffgram()

diffgram.auth(client_id = settings.CLIENT_ID,
			  client_secret = settings.CLIENT_SECRET,
			  project_string_id = settings.PROJECT_STRING_ID)


# Two example "instances" an instance is a single instance of an annotation

instance_alpha = {
					'type': 'box',
					'name': 'cat',
					'x_max': 128, 
					'x_min': 48,
					'y_min': 97,
					'y_max': 128
					}

instance_bravo = {
					'type': 'box',
					'name': 'cat',
					'x_max': 128, 
					'x_min': 1,
					'y_min': 1,
					'y_max': 128
				}


image_packet = {'instance_list' : [instance_alpha, instance_bravo],
				'media' : {
					'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					'type' : 'image'
					}
				}
	

diffgram.input_packet_single(image_packet)
