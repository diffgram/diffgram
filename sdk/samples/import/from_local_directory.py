from diffgram import Diffgram
import glob

project = Diffgram(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

directory_path = "../images_test/*"

path_list = glob.glob(directory_path)


for path in path_list:

	file = project.file.from_local(path)

	print(file.id)
