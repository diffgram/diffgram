import settings
from diffgram.core.core import Project

diffgram = Project()

diffgram.auth(client_id = settings.CLIENT_ID,
			  client_secret = settings.CLIENT_SECRET,
			  project_string_id = settings.PROJECT_STRING_ID)



config = {
	"instance_type": "box",
	"name": "Ferncat",
	"review_by_human_freqeuncy": "every_3rd_pass",
	"share_type": "Market",
	"type": "Normal"
}


job = diffgram.new_job(config = config)


# file_list = None		# TODO get file list from project

# Option to directly add new packets?
# Would that just be part of import?
# (ie a pass job_id to import, and a flag saying
# Add directly to job...

# Or doing this from existing files
# job.update_file_list(file_list = file_list)


image_packet = {'media' : {
					'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
					'type' : 'image'
					}
				}

diffgram.input_packet_single(image_packet = image_packet,
							 job = job)


diffgram.guide_new()

job.bid_default(per_instance = 0.09)


# Export download returns a call back url for the file?

# diffgram.export.generate()

job.status()


# Get results (ie instances) of a specific task
# ie pass task_id, and get instances back...

