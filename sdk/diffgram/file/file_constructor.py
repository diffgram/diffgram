
from diffgram.file.file import File
from diffgram.convert.convert import convert_label


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
			media_type="image"):
		"""
		WIP
		"""

		packet = {'media' : {}}
		packet['media']['url'] = url
		packet['media']['type'] = media_type

		self.import_packet(packet = packet)

		file = File()
		
		return file
		

	def from_diffgram_hash():

		pass

	

	def import_packet(
		self, 
		packet,
		job=None,
		convert_names_to_label_files=True,
		print_success=True
		):
		"""
		Import single packet of data of the form:

		image_packet_example
		{'instance_list' : 
			[instance_alpha,    # Array of instance dicts as defined below
				instance_bravo,
				... n instances],
		'media' : {
			'url' : "https://something",
			'type' : 'image'   # ['image', 'video']
			}
		}

		video_packet_example 
		{'frame_packet_map' : {
			0 : frame_packet,    # Where the key is the integer of the 
								  frame of the video, 0 indexed.
			6 : frame_packet,
			9 : frame_packet
		},
		'media' : {
			'url' : "https://something",
			'type' : 'video'
			}
		}

		instance_example
		{  'type': 'box', # options ['tag', 'box', 'polygon']
			label_file: { 
				id: Integer   # Diffgram label_file id. 
								accessible through diffgram.get_label_file_dict() See sample
			}
			'x_max': 128, Integer
			'x_min': 1,
			'y_min': 1,
			'y_max': 128,
			'points': [] # Required for polygon more on this coming soon
			'number': 0  # A number is optional, and only relates to video instances
		}


		Validates basics of packet form
		and makes request to /input/packet endpoint.

		"""

		if type(packet) != dict:
			raise Exception("packet is not a dict")

		if "media" not in packet:
			raise Exception(" 'media' key is not defined in packet.")  

		if "url" not in packet["media"]:
			raise Exception(" 'url' key is not defined in packet['media'] .")

		# TODO determine if local path or url, for now assume it's a URL?

		media_type = packet["media"].get("type", None)
		if not media_type:
			raise Exception(" 'type' key is not defined in packet['media'] use one of ['image', 'video']")
		# QUESTION should we default this to "image"

		instance = None

		if media_type == "image":	
			instance = self.check_instance_list(packet)

			if instance:
				if convert_names_to_label_files is True:
					# Convert "name" label (ie == "cat") to Diffgram label_file id
					for index, instance in enumerate(packet["instance_list"]):
	
						instance = convert_label(instance, instance["name"])
						packet["instance_list"][index] = instance


		if media_type == "video":
			if "frame_packet_map" not in packet:
				raise Exception(" 'frame_packet_map' key is not defined in packet")

			if type(packet["frame_packet_map"]) != dict:
				raise Exception("instance_list is not a dict")

			# CAREFUL frame_packet not packet
			for frame, frame_packet in packet["frame_packet_map"].items():
				if type(frame) != int:
					raise Exception("frame is not a integer")
		
				instance = self.check_instance_list(frame_packet)

				break

		# Test one of the instances
		# QUESTION Should we be testing all? User option maybe?
		# (Otherwise invalid ones get discarded when it hits API)

		if instance:
			instance_type = instance.get("type", None)
			if not instance_type:
				raise Exception(" type is not defined in the first instance \
									of instance_list. Options are 'tag', 'box', 'polygon'.")

			if instance_type not in ['tag', 'box', 'polygon']:
				raise Exception(" invalid instance type. Options are 'tag', 'box', 'polygon'.")

			if "label_file" not in instance:
				raise Exception(" label_file is not defined in the first instance \
									of instance_list. ")

			if "id" not in instance["label_file"]:
				raise Exception(" label_file is not defined in the first instance \
									of instance_list. ")


		if job:
			packet["job_id"] = job.id
			packet["mode"] = "attach_to_job"

		endpoint = "/api/v1/project/" + self.client.project_string_id + "/input/packet"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = packet)

		self.client.handle_errors(response)
		
		data = response.json()

		# TODO return file info

		if data["log"]["success"] is True:
			if print_success is True:
				print("Packet success")



	def check_instance_list(self, packet):

		# instance list is optional

		if "instance_list" in packet:

			if type(packet["instance_list"]) != list:
				raise Exception("instance_list is not array like")

			if len(packet["instance_list"]) == 0:
				raise Exception("'instance_list' is empty")
	
			return packet["instance_list"][0]

		return None


	def import_bulk():
		"""
		Import multiple packets
		FUTURE	
			Accept a dict of packets
			Each packet is defined as
			{ packet_id : { packet }}

		"""
		pass

