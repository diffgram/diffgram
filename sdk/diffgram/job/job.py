from copy import deepcopy


class Job():


	def __init__(self,
			     client,
				 job = None):

		self.client = deepcopy(client)

		if self.client.project_string_id is None:
			raise Exception("\n No project string id in client.")

		if job:
			self.id = job.id
			self.name = job.name
			self.status = job.status
			self.created_time = job.created_time


	def new(self,
			name,
			instance_type = "box",
			share = "project",
			job_type = "Normal",		
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

		my_job = {
			'name': name,
			'instance_type': instance_type,
			'share': share,
			'type': job_type
			}

		endpoint = "/api/v1/project/" + self.client.project_string_id + \
				   "/job/new"

		response = self.client.session.post(
						self.client.host + endpoint,
						json = my_job)

		self.client.handle_errors(response)

		data = response.json()

		if data.log.success == True:	

			job = Job(
					client = self.client,
					job = data.job)


		if file_list:

			# Careful we want to call job here not self
			# Since job will have a different id
			# self is constructor

			job.file_update(file_list = file_list)


		if launch is True:

			job.launch()

		if guide:

			job.guide_update(guide = guide)


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

		update_dict = {'file_list_selected' : file_list,
					   'job_id' : self.id,
					   'add_or_remove' : add_or_remove}

		response = self.client.session.post(self.client.host + endpoint,
									 json = update_dict)
		
		self.client.handle_errors(response)

		data = response.json()

		if data.log.success == True:
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

		if data.log.success == True:
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
					   'update_or_remove' : update_or_remove}

		response = self.client.session.post(self.client.host + endpoint,
									 json = update_dict)
		
		self.client.handle_errors(response)

		data = response.json()

		if data.log.success == True:
			print("File update success")
			return True

		return False
