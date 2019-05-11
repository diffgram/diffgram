from diffgram import Project

project = Project(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret")

# Construct new training with all defaults

brain = project.train.start(method="object_detection",
						    name="my_model")

brain.check_status()

print(brain.status)
