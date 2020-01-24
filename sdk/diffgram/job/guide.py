

class Guide():


	def __init__(self,
			     client = None,
				 guide = None):
		"""
		Jan 20, 2020
		Constructor and object...
			different pattern from File...
		"""

		self.client = client

		if self.client:
			if self.client.project_string_id is None:
				raise Exception("\n No project string id in client.")

		# Assumes dictionary (ie from response.data.guide)
		if guide:
			self.id = guide.get('id')
			self.name = guide.get('name')
			self.time_created = guide.get('time_created')


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

		print("New guide success")

		guide = Guide(guide = data.get('guide'),
					  client = self.client)

		return guide


	def update():
		pass
		
		# TODO method to update existing guide data ie name description etc.