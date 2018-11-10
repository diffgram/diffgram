
def import_bulk():
	"""
	Import multiple packets
	FUTURE	
		Accept a dict of packets
		Each packet is defined as
		{ packet_id : { packet }}

	"""
	pass


def single(self, packet):
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
		instance = check_instance_list(packet)

	if media_type == "video":
		if "frame_packet_map" not in packet:
			raise Exception(" 'frame_packet_map' key is not defined in packet")

		if type(packet["frame_packet_map"]) != dict:
			raise Exception("instance_list is not a dict")

		# CAREFUL frame_packet not packet
		for frame, frame_packet in packet["frame_packet_map"].items():
			if type(frame) != int:
				raise Exception("frame is not a integer")
		
			instance = check_instance_list(frame_packet)

			break

	# Test one of the instances
	# QUESTION Should we be testing all? User option maybe?
	# (Otherwise invalid ones get discarded when it hits API)

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

	endpoint = "/api/v1/project/" + self.project_string_id + "/input/packet"

	response = self.session.post(self.host + endpoint, 
								 json = packet)
	data = response.json()

	if data["log"]["success"] is False:
		raise Exception(data["log"]["errors"])



def check_instance_list(packet):
	if "instance_list" not in packet:
		raise Exception(" 'instance_list' key is not defined in packet")

	if type(packet["instance_list"]) != list:
		raise Exception("instance_list is not array like")

	if len(packet["instance_list"]) == 0:
		raise Exception("'instance_list' is empty")
	
	return packet["instance_list"][0]