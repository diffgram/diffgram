from diffgram import Diffgram

project = Diffgram(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

# Replace with your brain name, or leave blank to get latest
# Must set local flag to True
brain = project.get_model(
			name = None,
			local = True)

# Local, replace with yoru path
path = "A:/Sync/work/20190311_200900.jpg"

inference = brain.predict_from_local(path)

instance = inference.instance_list[0]

print(instance.location)
print(instance.score)
print(instance.label)