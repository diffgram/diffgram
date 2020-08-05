import random

from diffgram import Project
from diffgram.file.file_constructor import FileConstructor


def mock_box_from_external_format(
		sequence_number: int = None,
		name : str = None):

	return {
		"name" : name,
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

	name_list = ["cat", "another"]


	for i in range(number_of_frames):

		frame_packet_map[i] = []

		for j in range(1, number_of_sequences + 1):

			for name in name_list:

				frame_packet_map[i].append(mock_box_from_external_format(
					sequence_number = j,
					name = name)
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
			number_of_frames = 20,
			number_of_sequences = 2)

	result = project.file.from_url(
		signed_url,
		media_type="video",
		frame_packet_map=frame_packet_map
	)

	# TODO get file and then assert it exists



def test_existing_instances_image(project):

	signed_url = "https://storage.googleapis.com/diffgram_public/example_data/000000001323.jpg"

	instance_list = []

	for i in range(3):
		instance_list.append(
		   mock_box_from_external_format(name = "cat"))

	result = project.file.from_url(
		signed_url,
		media_type="image",
		instance_list=instance_list
	)


def test_expect_failure_no_url(project):
	"""
	Actually more testing API since exists so won't throw
	"""
	result = project.file.from_url(
		url = None,
		media_type="video",
		frame_packet_map={}
	)


def test_file_update(project):

	id = 787
	file = project.file.get_by_id(id = id)

	frame_packet_map = mock_frame_packet_map(
			number_of_frames = 20,
			number_of_sequences = 2)

	file.update(
		frame_packet_map = frame_packet_map
		)



test_file_update(project)

#test_expect_failure_no_url(project)

#test_video_packet_conversion(project)

#test_existing_video_instances(project)

#test_existing_instances_image(project)
