from ..regular.regular import refresh_from_dict
from diffgram.file.file import File


class Task():
	"""

	"""

	def __init__(
		self,
		client = None,
		id = None):

		self.client = client
		self.id = id
		self.file = None


	def __factory_create_object_from_json(task_in_json):
		"""

		In the current context a user doesn't create a new 
		File directly, the system creates a file at import
		and/or when copying / operating on a file.
		"""
		
		task = Task()
		refresh_from_dict(task, task_in_json)

		if task.file:
			task.file = File.new(
				client = self.client,
				file_json = task.file)

		return task


	def update():
		"""
		Update task, ie meta information
		"""
		raise NotImplemented


	def update_file(
			self,
			frame_packet_map: dict = None,
			):

		# TODO could abstract code block L225 file_constructor

		raise NotImplemented


	def serialize(self):

		return {
			'id' : self.id
			}


	def get_by_id(self, id: int):
		"""

		"""

		endpoint = "/api/v1/task"

		spec_dict = {
			'task_id': id,
			'builder_or_trainer_mode': 'builder'
			}

		response = self.client.session.post(
			self.client.host + endpoint,
			json = spec_dict)
		
		self.client.handle_errors(response)

		response_json = response.json()

		return Task.__factory_create_object_from_json(
					task_in_json = response_json.get('task'))
