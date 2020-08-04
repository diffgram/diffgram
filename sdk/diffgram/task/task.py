from ..regular.regular import refresh_from_dict


class Task():
	"""

	"""

	def __init__(
		self,
		id = None):

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
			task.file = refresh_from_dict(task.file, task.file)

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
		WIP for refreshing from server side.
		"""

		raise NotImplemented
