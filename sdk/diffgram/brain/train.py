from copy import deepcopy
from diffgram.brain.brain import Brain


class Train():

	def __init__(self, client):

		# If someone calls auth on client
		# We don't want existing models effected.

		self.client = deepcopy(client)

		if self.client.project_string_id is None:
			raise Exception("\n Client must be authenticated use client.auth()")



	def start(
			self,
			name,
			method = "object_detection",
			directory_id = None
			):

		"""
		name, string, name of new Brain
		method, string

		returns class Brain object
		"""

		request = {}
		request['ai_name'] = name
		request['training_options'] = {}
		request['directory_id'] = directory_id

		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
			"/machine_learning/training/run"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		brain = Brain(
					self.client,
					name = data['ai']['name'],
					id = data['ai']['id'])

		return brain

