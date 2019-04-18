from copy import deepcopy


class Guide():


	def __init__(self,
			     client,
				 guide = None):

		self.client = deepcopy(client)

		if self.client.project_string_id is None:
			raise Exception("\n No project string id in client.")

		if guide:
			self.id = guide.id
			self.name = guide.name
			self.time_created = guide.time_created


	def new(
			self, 
			name,
			description_markdown
			):
		"""

		Arguments
			self,
		
		Expects

		Returns

		"""
	
		endpoint = "/api/v1/project/" + self.client.project_string_id + \
				   "/guide/new"

		request = {'name' : name,
				   'description_markdown' : description_markdown}

		response = self.client.session.post(
						self.client.host + endpoint,
						json = request)
		
		self.client.handle_errors(response)

		data = response.json()

		if data["log"]["success"] == True:
			print("New guide success")


	def update():
		pass
		
		# TODO method to update existing guide data ie name description etc.