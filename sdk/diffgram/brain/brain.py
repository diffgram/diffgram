

class Brain():

	def __init__(self, client):

		self.client = client

		if self.client.project_string_id is None:
			raise Exception("\n Client must be authenticated use client.auth()")

		self.name = None
		self.id = None


	def predict(self, file):
		"""

		returns an inference object
		"""

		# main 

		print(file.id)

		endpoint = "/api/v1/project/" + self.client.project_string_id + "/input/packet"

		response = self.client.session.post(self.client.host + endpoint, 
											json = file.id)

		data = response.json()

		print(data)

