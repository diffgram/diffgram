from diffgram import Diffgram
import settings

"""
Most minimal example of creating and launching a new job.

"""
project = Diffgram(
			project_string_id = "replace_with_project_string",
			client_id = "replace_with_client_id",
			client_secret = "replace_with_client_secret"	)

path = "file_path"

file = project.file.from_local(path)
	
job = project.job.new(
		name = "my job from SDK",
		file_list = [file],
		launch = True
		)

