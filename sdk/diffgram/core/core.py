import requests

from diffgram import __version__

from diffgram.file.view import get_label_file_dict
from diffgram.core.directory import get_directory_list
from diffgram.core.directory import set_directory_by_name
from diffgram.convert.convert import convert_label
from diffgram.label.label_new import label_new

from diffgram.core.directory import Directory
from diffgram.job.job import Job
from diffgram.job.guide import Guide
from diffgram.brain.brain import Brain
from diffgram.file.file_constructor import FileConstructor
from diffgram.file.file import File
from diffgram.brain.train import Train
from diffgram.export.export import Export
from diffgram.task.task import Task


class Project():


	def __init__(
		self,
		project_string_id,
		client_id = None, 
		client_secret = None,
		debug = False,
		staging = False
		):

		self.session = requests.Session()
		self.project_string_id = None

		self.debug = debug
		self.staging = staging

		if self.debug is True:
			self.host = "http://127.0.0.1:8085"
			print("Debug", __version__)
		elif self.staging is True:
			self.host = "https://20200110t142358-dot-walrus-dot-diffgram-001.appspot.com/"
		else:
			self.host = "https://diffgram.com"

			# TODO support for staging URLs...

		self.directory_id = None
		self.name_to_file_id = None

		self.auth(
			project_string_id = project_string_id,
			client_id = client_id, 
			client_secret = client_secret)

		self.file = FileConstructor(self)
		self.train = Train(self)
		self.job = Job(self)
		self.guide = Guide(self)
		self.directory = Directory(self)
		self.export = Export(self)
		self.task = Task(client = self)


	def get_label(
			self,
			name=None,
			name_list=None):
		"""
		name, str
		name_list, list, optional

		Name must be an exact match to label name.

		If a name_list is provided it will construct a list of
		objects that match that name.

		Returns 
			None if not found.
			File object of type Label if found.
			List of File objects if a name_list is provided.
		"""
		if self.name_to_file_id is None:
			self.get_label_file_dict()

		if name_list:
			out = []
			for name in name_list:
				out.append(self.get_label(name))
			return out

		id = self.name_to_file_id.get(name)

		if id is None:
			return None

		file = File(id = id)
		return file


	def get_model(
			self,
			name = None,
			local = False):


		brain = Brain(
					client = self,
					name = name,
					local = local
					)

		return brain


	def handle_errors(self, 
				      response):

		"""
		Upon a bad request (400), our error log contains 
	    good information to raise.

		We also catch a few more common codes to
		try and print simpler messages.

		Otherwise expects this to be caught by raise_for_status()
		if applicable
		https://2.python-requests.org/en/master/_modules/requests/models/#Response.raise_for_status
		
		This is under the assumption that we generaly call response.json()
		after this, and that fails in poor way if there is no json available.
		"""

		# Default
		if response.status_code == 200:
			return

		# Errors
		if response.status_code == 400:
			try:
				raise Exception(response.json()["log"]["error"])
			except:
				raise Exception(response.text)

		if response.status_code == 403:
			raise Exception("Invalid Permission", response.text)

		if response.status_code == 404:
			raise(Exception("404 Not Found" + response.text))

		if response.status_code == 429:
			raise Exception("Rate Limited. Please add buffer between calls eg time.sleep(1). Otherwise, please try again later. Else contact us if this persists.")

		if response.status_code == 500:
			raise Exception("Internal error, please try again later.")

		raise_for_status = response.raise_for_status()
		if raise_for_status:
			Exception(raise_for_status)



	def auth(self, 
			project_string_id,
			client_id = None, 
			client_secret = None,
			set_default_directory = True,
			refresh_local_label_dict = True
			):
		"""
		Define authorization configuration

		If no client_id / secret is provided it assumes project is public
		And if project isn't public it will return a 403 permission denied.

		Arguments
			client_id, string
			client_secret, string
			project_string_id, string

		Returns
			None

		Future
			More gracefully intial setup (ie validate upon setting)
		"""
		self.project_string_id = project_string_id

		if client_id and client_secret:
			self.session.auth = (client_id, client_secret)
			
		if set_default_directory is True:
			self.set_default_directory()

		if refresh_local_label_dict is True:
			# Refresh local labels from Diffgram project
			self.get_label_file_dict()



	def set_default_directory(self, 
						     directory_id=None):
		"""
		-> If no id is provided fetch directory list for project
		and set first directory to default.
		-> Sets the headers of self.session

		Arguments
			directory_id, int, defaults to None

		Returns
			None

		Future
			TODO return error if invalid directory?

		"""

		if directory_id:
			# TODO check if valid?
			# data = {}
			# data["directory_id"] = directory_id
			self.directory_id = directory_id
		else:

			data = self.get_directory_list()

			self.default_directory = data['default_directory']
			
			# Hold over till refactoring (would prefer to
			# just call self.directory_default.id
			self.directory_id = self.default_directory['id']

			self.directory_list = data["directory_list"]

		self.session.headers.update(
			{'directory_id': str(self.directory_id)})


# TODO review not using this pattern anymore

setattr(Project, "get_label_file_dict", get_label_file_dict)
setattr(Project, "get_directory_list", get_directory_list)
setattr(Project, "convert_label", convert_label)
setattr(Project, "label_new", label_new)
setattr(Project, "set_directory_by_name", set_directory_by_name)
