
from diffgram.file.file import File


class FileConstructor():
	"""

	Construct files and communicate with client

	Caution class needs client in order to do effective communication
	with server


	"""

	def __init__(self, client):

		self.client = client

		

	def from_url(
			self,
			url, 
			type):
		"""

		"""

		file = File()

		# Basically this

		#client.input_packet_single(image_packet)
		endpoint = "/api/v1/project/" + self.client.project_string_id + "/input/packet"

		response = self.client.session.post(self.client.host + endpoint, 
											json = url)

		data = response.json()

		print(data)

		return file
		

	def from_diffgram_hash():

		pass
