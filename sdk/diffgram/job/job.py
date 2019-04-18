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

			job.file_update(file_list = file_list)


		if launch is True:

			job.launch()

		if guide:

			pass
			# TODO attach guide to job here


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

		Returns

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

