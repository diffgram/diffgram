
from google.cloud import storage
import sys
import time, tempfile

from shared.helpers import sessionMaker
from shared.database.project import Project

from shared.helpers.permissions import get_gcs_service_account
from methods import routes
from shared.settings import settings

from shared.permissions.project_permissions import Project_permissions

from imageio import imwrite
from imageio import imread
from shared.image_tools import imresize

import numpy as np
from PIL import Image, ImageDraw
from shared.data_tools_core import Data_tools


data_tools = Data_tools().data_tools

# Newly created file upload
ML_bucket = data_tools.ML_bucket

# Images are in bucket
bucket = data_tools.bucket
# Support walrus, not clear exactly why we want this seperetly here???

@routes.route('/api/walrus/project/<string:project_string_id>/data/masks/generate',
			  methods=['GET'])
@Project_permissions.user_has_project(["admin"])
def generate_mask_by_project_id(project_string_id):


	# TODO use a thread, this is a long running process

	semantic_segmentation_data_prep = Semantic_segmentation_data_prep()

	with sessionMaker.session_scope() as session:

		project = Project.get(session, project_string_id)
		type = "joint"
		#type = "binary"
		semantic_segmentation_data_prep.generate_mask_core(
			session, project, type)

	return "ok", 200, {'ContentType':'application/json'}



class Semantic_segmentation_data_prep():
	"""

	create as new instance so temp dir for each run?

	"""

	def __init__(self):
		self.temp = tempfile.mkdtemp()


	def generate_mask_core(
			self, 
			session, 
			project, 
			file_list,
			label_dict = None,
			type="binary"):
	
		"""
		Program purpose: Convert annotated points_local into segmented colours
		for use as ground truth for neural network

		Default mode == binary

		Saves images in bit depth == 8
		Where
		background == 0
		class == 1

		label_dict only required for type == "joint"?
		Why? -> So we can have mask values increase in series
		instead of using ids for example

		1. Collect polygons to generate
		2. Do generation
		3. Save images to directory

		Could be called internally or externally?
		Based on images in a project right?

		"""
		print("[Semantic masks] init", file=sys.stderr)
		self.expiration = int(time.time() + 2592000)  # 1 month

		for file in file_list:

			image_dir = settings.PROJECT_IMAGES_BASE_DIR + \
				str(project.id) + "/" + str(file.image_id)
			raw_image_blob = bucket.blob(image_dir)

			temp_file = tempfile.NamedTemporaryFile(delete=True)

			raw_image_blob.download_to_file(temp_file)

			image_numpy = imread(temp_file)
			temp_file.close()

			if type == "binary":
				self.generate_mask_binary(
					session, 
					file,
					project)

			if type == "joint":		

				self.generate_mask_joint(
					session, 
					file,
					project, 
					label_dict)

		print("[Semantic masks] success", file=sys.stderr)


	def generate_mask_binary(self, session, image, project):
		
		# TODO review, no long have image, have 
		# file with instance list

		for i, polygon in enumerate(image.polygons):   
			
			if polygon.soft_delete == True:
				continue

			"""
			Image draw expects a tuple (value, value) ie (x, y)
			Where as data is stored as dict {'x': value, 'y': value)
			"""
			points_local = []
			for point in polygon.points['points']:
				points_local.append((point['x'], point['y']))


			# TODO review options for saving / using 1 bit array here
			#background = Image.new('1', (image_numpy.shape[1], image_numpy.shape[0]), 0)

			# TODO
			# Also store minimum / max values for use in bounding box features...

			"""
			Careful with shapes here, scipy reads it as is (height, width)
			Where as Image.new() expects the INVERSE (width, height)
			"""

			background = Image.new('L', (image.width, image.height), 0)
			if len(points_local) >= 2:
				ImageDraw.Draw(background).polygon(points_local, outline=255, fill=255)
			background = np.array(background)

			file_name = self.temp + "/" + str(i) + ".png" 

			# Could do 0 index thing but this preserves which polygon it'session referring to... not sure

			mask_blob_name = settings.PROJECT_IMAGES_BASE_DIR + \
			str(project.id) + "/semantic_segmentation_masks/" + str(image.id) + '/' + str(i) + ".png" 

			imwrite(file_name, background.astype(np.uint8))
			blob = ML_bucket.blob(mask_blob_name)

			blob.upload_from_filename(file_name, content_type = "image/png")

			# TODO list of of mask urls?
			# image.url_annotation_example = blob.generate_signed_url(expiration = self.expiration)


			polygon.mask_url = blob.generate_signed_url(expiration = self.expiration)

			# TODO review this
			# Each polygon can only have one class so what are we doing here?

			polygon.mask_blob_name['list'].append(mask_blob_name)
			session.add(polygon)



	def generate_mask_joint(
			self, 
			session, 
			file	, 
			project, 
			label_dict):

		"""
		each image stores a pixel mask where
		255 = background
		0 - 254 == classes
		"""
		
		background = 255

		image = file.image

		mask = Image.new('L', (image.width, image.height), background)
		drawer = ImageDraw.Draw(mask)

		# TODO pull instances useing customer query
		# so don't have to iterate through things like soft delete
		# or polygon etc?

		start_time = time.time()

		for instance in file.instance_list:                  
			
			# QUESTION are we assuming polygons for now here?

			if instance.type != "polygon":
				continue

			if instance.soft_delete == True:
				continue


			# Image draw expects a tuple (value, value) ie (x, y)
			# Where as data is stored as dict {'x': value, 'y': value)
			points_local = []
			for point in instance.points['points']:
				points_local.append((point['x'], point['y']))

			# So if we use label id here
			# Label id is shared accross polygons
			# label_dict is an index starting at 1
			# This keeps values consistant up to ~255 classes?
			# Do we need to -1 to 0 index it? or does that matter?
			#print(type(polygon.label.id))
			# print(label_dict.keys())
			#fill = label_dict[int(instance.label_file_id)]
			class_id = label_dict.get(str(instance.label_file_id))
			if class_id is None:
				class_id = label_dict.get(int(instance.label_file_id))
			#error case can't find class id....
			if class_id is None:
				class_id = 99999

			if len(points_local) >= 2:
				drawer.polygon(points_local, fill=class_id)
		
		#print("Time for instance list", time.time() - start_time)
		
		mask = np.array(mask)

		file_name = self.temp + "/" + str(image.id) + ".png" 

		# Is this the path we want???
		# OR should we save by time stamp? I guess export dir is already unique 

		# Also we don't have export here at the moment... that's 
		# why this is here...

		blob_name = settings.EXPORT_DIR + \
			str(project.id) + "/semantic_segmentation_masks/joint/" + \
			str(file.id) + ".png" 

		imwrite(file_name, mask.astype(np.uint8))
		blob = ML_bucket.blob(blob_name)
		blob.upload_from_filename(file_name, content_type = "image/png")

		# TODO verify if this close frees up memory as expected.
		file_name.close()

		# Carful, need to save this with the file,
		# since mask could be differnt for different files...

		#image.mask_joint_url = blob.generate_signed_url(expiration = self.expiration)
		
		file.mask_joint_blob_name = blob_name
		
		session.add(file)
	
					 
	def clean(self):

		try:
			shutil.rmtree(self.temp)  # delete directory
		except OSError as exc:
			if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
				raise  # re-raise exception
