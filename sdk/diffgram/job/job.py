

class Job():


	def __init__(self,
			     client,
				 job = None):

		self.client = client

		if self.client.project_string_id is None:
			raise Exception("\n No project string id in client.")

		# TODO review way to set all properties 
		# from existing job update
		#self.name = job.name
		#self.status = job.status
		#self.created_time = job.created_time


	def serialize(self):

		return {
			'name': self.name,
			'instance_type': self.instance_type,
			'share': self.share,
			'type': self.type,
			'permission': self.permission,
			'field': self.field,
			'category': self.category,
			'review_by_human_freqeuncy': self.review_by_human_freqeuncy,
			'label_mode': self.label_mode,
			'passes_per_file': self.passes_per_file
		}

	def new(self,
			name,
			instance_type = "box",
			share = "Project",
			job_type = "Normal",	
			permission = "all_secure_users",
			field = "Other",
			category = "visual",
			review_by_human_freqeuncy = "every_3rd_pass",
			label_mode = "closed_all_available",
			passes_per_file = 1,
			file_list = None,
			guide = None,
			launch = False
			):
		"""

		Arguments
			self,
			config, a dict of job data
			launch, bool, Launch job after creation
		
		Expects

		Returns

		"""

		# QUESTION create job object eariler instead of after response?

		job = Job(client = self.client)

		job.name = name
		job.instance_type = instance_type
		job.share = {'type': share}
		job.type = job_type   # careful rename to type from job_type
		job.permission = permission
		job.field = field
		job.category = category
		job.review_by_human_freqeuncy = review_by_human_freqeuncy
		job.label_mode = label_mode
		job.passes_per_file = passes_per_file


		endpoint = "/api/v1/project/" + self.client.project_string_id + \
				   "/job/new"

		response = self.client.session.post(
						self.client.host + endpoint,
						json = job.serialize())

		self.client.handle_errors(response)

		data = response.json()

		if data["log"]["success"] == True:	

			# TODO review better way to update fields
			job.id = data["job"]["id"]


		if file_list:

			# Careful we want to call job here not self
			# Since job will have a different id
			# self is constructor

			job.file_update(file_list = file_list)


		if guide:

			job.guide_update(guide = guide)


		if launch is True:

			job.launch()


		return job



	def file_update(
			self, 
			file_list,
			add_or_remove = "add"
			):
		"""

		Arguments
			self,
			file_list, list of files,
			add_or_remove, either "add" or "remove"
		
		Expects

		Returns

		"""
	
		endpoint = "/api/v1/project/" + self.client.project_string_id + \
				   "/job/file/attach"

		file_list = [file.serialize() for file in file_list]

		update_dict = {'file_list_selected' : file_list,
					   'job_id' : self.id,
					   'add_or_remove' : add_or_remove}

		response = self.client.session.post(self.client.host + endpoint,
									 json = update_dict)
		
		self.client.handle_errors(response)

		data = response.json()

		if data["log"]["success"] == True:
			print("File update success")


	
	def launch(
			self
			):
		"""

		Arguments
			self,
		
		Expects
			None

		Returns
			True if success

		"""
	
		endpoint = "/api/v1/job/launch"

		request = {'job_id' : self.id}

		response = self.client.session.post(
						self.client.host + endpoint,
						json = request)
		
		self.client.handle_errors(response)

		data = response.json()

		if data["log"]["success"] == True:
			print("Launched")
			return True

		return False



		
	def guide_update(
			self, 
			guide,
			kind = "default",
			action = "update"
			):
		"""

		Arguments
			self,
			guide, class Guide object
			kind options ["default", "review"]
			update_or_remove options ["update", "remove"]
		
		Expects

		Returns
			None, prints update

		"""
	
		endpoint = "/api/v1/guide/attach/job"

		update_dict = {'guide_id' : guide.id,
					   'job_id' : self.id,
					   'kind' : kind,
					   'update_or_remove' : action}

		response = self.client.session.post(self.client.host + endpoint,
									 json = update_dict)
		
		self.client.handle_errors(response)

		data = response.json()

		if data["log"]["success"] == True:
			print("Guide update success")
			return True

		return False


	def export_results(
			self, 
			kind = 'Annotations',
			return_type = "data"
			):
		"""

		Arguments
			self,
			kind, string, in ["Annotations", "TF Records"]
			return_type, string, in ["url", "data"]

		# Note that the "data" return type is for kind "Annotations"
		# The data is expected to be returned in JSON format
		
		Expects

		Returns

		"""
	
		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
				   "/export/to_file"

		# TODO not a fan of "return_type" variable name
		# Also, can we map this into a more "automatic" 
		# Default? ie tf records being a url etc..

		spec_dict = {
			'job_id': self.id,
			'kind' : kind,
			'source' : "job",
			'file_comparison_mode' : "latest",
			'directory_id' : None,
			'masks' : False,
			'return_type' : return_type,
			'wait_for_export_generation' : True
			}

		response = self.client.session.post(self.client.host + endpoint,
									 json = spec_dict)
		
		self.client.handle_errors(response)

		data = response.json()

		return data
