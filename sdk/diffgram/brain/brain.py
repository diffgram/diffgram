from copy import deepcopy


class Brain():

	def __init__(self, client):

		# If someone calls auth on client
		# We don't want existing models effected.

		self.client = deepcopy(client)

		if self.client.project_string_id is None:
			raise Exception("\n Client must be authenticated use client.auth()")

		self.name = None
		self.id = None


	def predict(self, file):
		"""

		WIP for passing file object
		in case where diffgram already has file.

		returns an inference object
		"""

		# main 

		print(file.id)

		endpoint = "/api/v1/project/" + self.client.project_string_id + "/input/packet"

		response = self.client.session.post(self.client.host + endpoint, 
											json = file.id)

		data = response.json()

		print(data)


	def predict_from_url(
			self,
			url):
		"""
		url, string, web end point to get file
		"""

		request = {}
		request['url'] = url
		request['ai_name'] = self.name

		endpoint = "/api/v1/project/" + self.client.project_string_id + \
			"/inference/from_url"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		# TODO create Inference() object...		
		# How we want to return / work with that

		self.client.handle_errors(response)

		if data["log"]["success"] is True:
			pass

		return None


	def predict_from_local(
			self,
			path):
		"""
		Make a prediction from a local file.
		Creates a Diffgram file object and runs prediction.

		This is roughly equal to running file.from_local() and predict()
	    but in one request to Diffgram (instead of two).

		path, string, file path
		"""

		files = {'file': open(path, 'rb')}

		options = {'immediate_mode' : 'True'}
				
		endpoint = "/api/v1/project/" +  self.client.project_string_id \
			+ "/inference/from_local"

		response = self.client.session.post(
			self.client.host + endpoint, 
			files = files,
			headers = options)

		self.client.handle_errors(response)
		
		data = response.json()

		# TODO handle creation of Inference and Instancte objects	

	def predict_from_file(
			self,
			file_id):
		"""
		file_id, int, diffgram file id

		Assumes singular file for now
		"""

		request = {}
		request['file_list'] = [{'id' : file_id}]
		request['ai_name'] = self.name
		request['wait_for_inference'] = True

		endpoint = "/api/project/" + self.client.project_string_id + \
			"/inference/add"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		# TODO create Inference() object...		
		# How we want to return / work with that

		self.client.handle_errors(response)

		if data["log"]["success"] is True:
			pass

		return None