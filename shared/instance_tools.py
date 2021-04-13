# OPEN CORE - ADD
import numpy as np
import time
from io import BytesIO
from imageio import imwrite
from shared.image_tools import imresize

import sys
import json
import os, requests, time, logging, yaml
import threading
import tempfile
from shared.settings import settings
from shared.shared_logger import get_shared_logger
from shared.data_tools_core import Data_tools

logger = get_shared_logger()

"""


When creating new instance
1. Use coordinates to get mask / crop to that specific size
2. Save new image thumbnail (ie 100x100)
3. Attach to that instance as a url

"""

data_tools = Data_tools().data_tools


class Instance_tools():

	def __init__(self):
		self.temp = tempfile.mkdtemp()


	def new_thumb_image_from_frame(
			self, 
			session,
			video,
			instance):
	
		# new
		if video.root_blob_path_to_frames:
			root_path = video.root_blob_path_to_frames
			# assumed to have trailing "/" 

			blob_path = root_path + str(instance.frame_number)
		
		# migration
		else:
			print("Used image path migration")
			if not instance.file.image:
				return False

			blob_path = self.get_migration_path(
				project = instance.file.project,
			    image = instance.file.image)

		image_np = data_tools.get_image(blob_path)

		cropped_image = self.crop_image(image_np, instance)
		if cropped_image is False:
			return False

		self.upload(session, instance, cropped_image)

		return True


	def get_migration_path(self, project, image):

		return settings.PROJECT_IMAGES_BASE_DIR + \
			str(project.id) + "/" + str(image.id)




	def crop_image(self, image, instance):
		"""

		"""
		x_min, y_min = instance.x_min, instance.y_min
		x_max, y_max = instance.x_max, instance.y_max
		print(x_min, y_min, x_max, y_max)
		logger.debug('Min Coordinates: ({},{})'.format(x_min, y_min))
		logger.debug('Max Coordinates: ({},{})'.format(x_max, y_max))
		cropped_image = image[y_min : y_max, x_min : x_max]

		# Maintain aspect ratio

		# Check for div by 0 errors
		if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
			return False

		ratio = min((160 / cropped_image.shape[0]), 
					(160 / cropped_image.shape[1]))

		shape_x = int(round(cropped_image.shape[0] * ratio))
		shape_y = int(round(cropped_image.shape[1] * ratio))

		resized_cropped_image = imresize(cropped_image, 
									(shape_x, shape_y))

		return resized_cropped_image

	def upload(self, session, instance, cropped_image):

		# We may want to save this to the instance
		# as well, but I think it would reduce other issues if we saved
		# it to the sequence instead?

		image_out_filename = self.temp + 'image_out.jpg'
		imwrite(image_out_filename, cropped_image)

		instance.preview_image_blob_dir = settings.PROJECT_INSTANCES_IMAGES_BASE_DIR + str(instance.id) + "/_thumb.jpg"

		data_tools.upload_to_cloud_storage(
			temp_local_path = image_out_filename,
			blob_path = instance.preview_image_blob_dir,
			content_type = 'image/jpg'
		)

		instance.preview_image_url = data_tools.build_secure_url(
			blob_name = instance.preview_image_blob_dir,
			expiration_offset = 2592000
		)
		session.add(instance)
