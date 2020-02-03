from ..regular.regular import refresh_from_dict


class Export():
	"""
	An export object is metadata. ie Status, etc.
	Exporting sample patterns:
	
	A) Call generate_export() from a job object (or directory coming soon)
	 It will return JSON or a URL directly and is blocking.

	 Note, we maintain generate_export() as options on Job() class
	 because the job id is the main thing needed to genrate the export
	 so it's more natural to call that then worry about passing the job
	 id to Export

	B) generate_export() can optionally return a class Export() object
	of which access_data() can be called.

	For more in depth discussion see:
	https://diffgram.readme.io/docs/export-walkthrough#section-export-generation-through-sdk


	"""

	def __init__(self,
			     client):

		self.client = client


	
	def get_by_id(self, id: int):
		"""
		WIP for refreshing from server side.
		"""

		raise NotImplemented


	def new(self, export_dict: dict) -> 'Export':
		"""
		New type Export() object from existing.
			Assumes the object exists correctly,
			ie does not refresh from server.

		If we just have an id we assume we call
			get_by_id()

		"""
		export = Export(client = self.client)
		refresh_from_dict(export, export_dict)
		return export


	def list(self):
		"""
		List existing in context of a project

		"""
		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
			   "/export/working_dir/list"

		response = self.client.session.get(self.client.host + endpoint)

		self.client.handle_errors(response)

		export_list_json = response.json().get('export_list')
		export_list = []

		if export_list_json:
			for export_json in export_list_json:
				export_list.append(self.new(export_json))

		return export_list


	def access_data(self,
		  return_type: str = "url",
		  format: str = "JSON"
		  ):
		"""
		Get existing data.
		This assumes the export generation has been successful,
		will raise if export is not complete.

		"""


		valid_return_types = ['url', 'data']

		if return_type not in valid_return_types:
			raise Exception("return_type options", valid_return_types)


		valid_format = ["JSON", "YAML"]

		if format not in valid_format:
			raise Exception("format options", valid_format)


		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
			   "/export/link"

		body_dict = {
			'id' : self.id,
			'return_type' : return_type,
			'format' : format}

		response = self.client.session.post(
			self.client.host + endpoint,
			json = body_dict)

		self.client.handle_errors(response)

		return response.json()
