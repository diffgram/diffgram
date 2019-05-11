from diffgram import Project

project = Project(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

# Two example box "instances" an instance is a single instance of an annotation

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

# Combine into image packet

image_packet = {'instance_list' : [instance_alpha, instance_bravo],
				'media' : {
					'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					'type' : 'image'
					}
				}
	

result = project.file.from_packet(image_packet)

print(result)
