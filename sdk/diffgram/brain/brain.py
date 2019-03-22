from copy import deepcopy

from diffgram.brain.inference import Inference


class Brain():

	def __init__(
			self, 
			client,
			name=None,
			id=None):

		# If someone calls auth on client
		# We don't want existing models effected.

		self.client = deepcopy(client)

		if self.client.project_string_id is None:
			raise Exception("\n Client must be authenticated use client.auth()")

		self.name = name
		self.id = id
		self.status = None


	def inference_from_response(
			self, 
			dict):

		# Assumes object detection
		# TODO condition on method

		inference = Inference(
			method = "object_detection",
			id = dict['id'],
			status = dict['status'],
			box_list = dict['box_list'],
			score_list = dict['score_list'],
			label_list = dict['label_list']
			)

		return inference


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

		self.client.handle_errors(response)

		inference = self.inference_from_response(data['inference'])
		return inference


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

		options = { 'immediate_mode' : 'True',
					'ai_name' : self.name}
				
		endpoint = "/api/v1/project/" +  self.client.project_string_id \
			+ "/inference/from_local"

		response = self.client.session.post(
			self.client.host + endpoint, 
			files = files,
			data = options)

		self.client.handle_errors(response)
		
		data = response.json()

		inference = self.inference_from_response(data['inference'])
		return inference

		# TODO handle creation of Inference and Instance objects	


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

		inference = self.inference_from_response(data['inference'])
		return inference


	def check_status(
		  self):
		"""
		

		"""

		request = {}
		request['ai_name'] = self.name

		endpoint = "/api/v1/project/" + self.client.project_string_id + \
			"/brain/status"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		self.status = data['ai']['status']
