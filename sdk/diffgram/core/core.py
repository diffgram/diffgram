import requests
from diffgram.input.packet import single
from diffgram.file.view import get_label_file_dict
from diffgram.file.directory import get_directory_list
from diffgram.convert.convert import convert_label
from diffgram.label.label_new import label_new


class Diffgram():


	def __init__(self,
				 debug = False):

		self.session = requests.Session()
		self.project_string_id = None

		self.debug = debug

		if self.debug is True:
			self.host = "http://127.0.0.1:8080"
			print(diffgram.__version__)
		else:
			self.host = "https://diffgram.com"

		self.directory_id = None
		self.name_to_file_id = None


	def auth(self, 
			client_id, 
			client_secret, 
			project_string_id,
			set_default_directory = True,
			refresh_local_label_dict = True
			):
		"""
		Define authorization configuration

		Arguments
			client_id, string
			client_secret, string
			project_string_id, string

		Returns
			None

		Future
			More gracefully intial setup (ie validate upon setting)
		"""
		self.session.auth = (client_id, client_secret)
		self.project_string_id = project_string_id

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

			self.directory_id = data["directory_list"][0]["id"]

		self.session.headers.update(
			{'directory_id': str(self.directory_id)})




setattr(Diffgram, "input_packet_single", single)
setattr(Diffgram, "get_label_file_dict", get_label_file_dict)
setattr(Diffgram, "get_directory_list", get_directory_list)
setattr(Diffgram, "convert_label", convert_label)
setattr(Diffgram, "label_new", label_new)