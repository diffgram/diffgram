import random

from diffgram import Project
from diffgram.file.file_constructor import FileConstructor


def mock_box_from_external_format(sequence_number: int = None):

	return {
		"name" : "cat",
		"number": sequence_number,
		"type": "box",
		"x_max": random.randint(500, 800),
		"x_min": random.randint(400, 499),
		"y_max": random.randint(500, 800),
		"y_min": random.randint(400, 499)
		}


def failing_instance_example():

	from diffgram.convert.convert import convert_label
	convert_label(None, {})
	

#failing_instance_example()


def mock_frame_packet_map(
		number_of_frames:int = None,
		number_of_sequences: int = 1
		):
	"""
	"""
		
	frame_packet_map = { }

	for i in range(number_of_frames):

		frame_packet_map[i] = []

		for j in range(1, number_of_sequences + 1):

			frame_packet_map[i].append(mock_box_from_external_format(
				sequence_number = j)
			)

	return frame_packet_map


def test_video_packet_conversion(project):
	"""
	To test this well we need an active project since we expect the 
	name_to_file thing to exist.
	"""
	frame_packet_map = mock_frame_packet_map(
			number_of_frames = 3)

	# assumes 0th frame available, and 0ths instance
	instance_list = frame_packet_map.get(0)

	instance_list = project.file.instance_list_label_strings_to_ids(
				instance_list = instance_list
				)

	example_instance = instance_list[0]
	assert example_instance is not None

	label_file_id = example_instance.get('label_file_id')
	assert label_file_id is not None
	assert isinstance(label_file_id, int)
	print(label_file_id)



def test_existing_video_instances(project):

	signed_url = "https://storage.googleapis.com/diffgram_public/example_data/challenge_videoTrim.mp4"

	frame_packet_map = mock_frame_packet_map(
			number_of_frames = 40,
			number_of_sequences = 1)

	result = project.file.from_url(
		signed_url,
		media_type="video",
		frame_packet_map=frame_packet_map
	)

	# TODO get file and then assert it exists


project = Project() 


#test_video_packet_conversion(project)

test_existing_video_instances(project)
