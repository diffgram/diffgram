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

