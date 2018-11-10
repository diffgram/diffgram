
from core.core import Diffgram
from sample_data import image_packet
from sample_data import video_packet


diffgram = Diffgram()

client_id = "replace_with_your_client_id"
client_secret = "replace_with_your_client_secret"
project_string_id = "replace_with_your_project_string_id"

diffgram.auth(client_id = client_id,
			  client_secret = client_secret,
			  project_string_id = project_string_id)


diffgram.set_default_directory()

diffgram.get_label_file_dict()


# Convert "name" label (ie == "cat") to Diffgram label_file id

for index, instance in enumerate(image_packet["instance_list"]):
	
	instance = diffgram.convert_label(instance, instance["name"])
	image_packet["instance_list"][index] = instance
	


def convert_sequence(instance, latest_number, external_track_label):
	"""
	Convert a sequence from an external id ie 'trackid' to integers unique per video.
	"""

	external_id = instance[external_track_label]

	number = instance.get('number', None)
	if number is None:

		existing_number = sequence_id_to_number.get(external_id, None)

		if existing_number:
			instance['number'] = existing_number
		else:
			instance['number'] = latest_number
			sequence_id_to_number[instance[external_track_label]] = latest_number
			latest_number += 1

		instance['external_id'] = external_id

	return instance, latest_number


sequence_id_to_number = {}
latest_number = 1
external_track_label = 'trackid'


for number, packet in video_packet['frame_packet_map'].items():

	for index, instance in enumerate(packet["instance_list"]):

		instance = diffgram.convert_label(instance, instance["name"])

		instance, latest_number = convert_sequence(instance, latest_number, external_track_label)

		video_packet['frame_packet_map'][number]['instance_list'][index] = instance




diffgram.input_packet_single(image_packet)
#diffgram.input_packet_single(video_packet)