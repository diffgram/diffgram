from diffgram.brain.inference import Inference


import tempfile

# TODO import these only if local prediction is needed
import cv2

try:
	import tensorflow as tf
except:
	print("Could not import tensorflow")

import numpy as np
import requests
import scipy.misc

import diffgram.utils.visualization_utils as vis_util


class Brain():

	def __init__(
			self, 
			client,
			name=None,
			id=None,
			local=False,
			use_temp_storage=True
			):
		"""
		client, project client object
		name, string, exact match for Project AI name
		local, bool, run model locally

		if local is true will perform additional setup work local_setup()

		"""

		self.client = client

		if self.client.project_string_id is None:
			raise Exception("\n No project string id in client.")

		self.name = name
		self.id = id
		self.status = None
		self.local = local
		self.method = None
		self.sub_method = None
		self.min_score_thresh = .5
		self.build_complete = None
		self.model_path = None
		self.image_to_run = None

		self.use_temp_storage = use_temp_storage
		self.local_model_storage_path = None

		if self.local is True:

			# These are only needed for local operations
			self.temp = tempfile.mkdtemp()

			self.local_setup()


	def inference_from_response(
			self, 
			dict):

		# Assumes object detection
		# TODO condition on method

		inference = Inference(
			method = "object_detection",
			id = dict['id'],
			status = dict['status'],
			box_list = dict['box_list'],
			score_list = dict['score_list'],
			label_list = dict['label_list']
			)

		return inference



	def predict_from_url(
			self,
			url):
		"""
		url, string, web end point to get file
		"""

		if self.local is True:
			raise Exception("Not supported for local models yet.")

		request = {}
		request['url'] = url
		request['ai_name'] = self.name

		endpoint = "/api/walrus/v1/project/" + self.client.project_string_id + \
			"/inference/from_url"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		self.client.handle_errors(response)

		inference = self.inference_from_response(data['inference'])
		return inference


	def predict_from_local(
			self,
			path):
		"""
		Make a prediction from a local file.
		Creates a Diffgram file object and runs prediction.

		This is roughly equal to running file.from_local() and predict()
		but in one request (instead of two).

		path, string, file path
		"""
		if self.local is True:

			self.image_to_run = open(path, "rb")

			# WIP 
			# TODO clean up, declare options for different types of expected inputs
			# this is for model that expects numpy array as input
			#self.image_np = scipy.misc.imread(path)
			#self.image_np = self.resize(self.image_np)

			# moved this here, was part of other thing prior
			self.image_to_run = self.image_to_run.read()

			self.run()

			inference = self.inference_from_local()

			return inference
			
		if self.local is False:

			files = {'file': open(path, 'rb')}

			options = { 'immediate_mode' : 'True',
						'ai_name' : self.name}
				
			endpoint = "/api/walrus/v1/project/" +  self.client.project_string_id \
				+ "/inference/from_local"

			response = self.client.session.post(
				self.client.host + endpoint, 
				files = files,
				data = options)

			self.client.handle_errors(response)
		
			data = response.json()

			inference = self.inference_from_response(data['inference'])
			
			return inference

			# TODO handle creation of Inference and Instance objects	

	def run(
		 self, 
		 image = None):

		if self.build_complete is False:
			return False

		if image:
			self.image_to_run = image

		with self.graph.as_default():
		
			# MUST HAVE compat.as_bytes for tf slim 
			# https://www.tensorflow.org/api_docs/python/tf/compat/as_bytes
			# https://stackoverflow.com/questions/46687348/decoding-tfrecord-with-tfslim

			self.image_to_run_expanded = tf.compat.as_bytes(self.image_to_run)

			self.image_to_run_expanded = np.expand_dims(self.image_to_run_expanded, axis=0)

			self.method = "object_detection"

			if self.sub_method == "default" or self.sub_method is None:

				self.run_object_detection()


		inference = self.inference_from_local()

		return inference

	
	def run_object_detection(self):

		(boxes, scores, classes, num) = self.sess.run(
			[self.detection_boxes, 
			 self.detection_scores, 
			 self.detection_classes, 
			 self.num_detections],
			 feed_dict = { 
				 self.image_tensor: self.image_to_run_expanded } )

		self.boxes = np.squeeze(boxes)
		self.scores = np.squeeze(scores)
		self.classes = np.squeeze(classes).astype(np.int32)

		#print(self.boxes, self.scores, self.classes)



	def nearest_iou(self, alpha, bravo):
	 
		_best_iou_hyper = .2

		for i in range(len(alpha.box_list)):
			
			best_iou = 0
			best_index = None

			# Find best IoU
			for j in range(len(bravo.box_list)):
				
				iou = Brain.calc_iou(alpha.box_list[i], bravo.box_list[j])

				if iou >= best_iou:
					best_iou = iou
					best_index = j
			
			if best_index is None:
				continue

			# handle large boxes, is the threat entirely inside the box?
			alpha_box = alpha.box_list[i]

			bravo_box = bravo.box_list[best_index]

			if best_iou > _best_iou_hyper or best_iou > .01 and \
				alpha_box[1] < bravo_box[1] and \
				alpha_box[3] > bravo_box[3] and \
				alpha_box[0] < bravo_box[0] and \
				alpha_box[2] > bravo_box[2]:

				# Assumes boxes have been thresholded already, 
				# This way threshold applies to nearest search too

				class_id = bravo.label_list[best_index]

				nearest_alpha_box = bravo.box_list[best_index]
			
				# for stats
				#self.average_iou = ( (best_iou + self.average_iou  ) / 2)

				# Where best_index is which bravo one
				# is "in" which i index

				print("alpha is in bravo", i, "in", best_index)



	@staticmethod
	def calc_iou(box_a, box_b):
		# Calculate intersection, i.e. area of overlap between the 2 boxes (could be 0)
		# http://math.stackexchange.com/a/99576
		x_overlap = max(0, min(box_a[2], box_b[2]) - max(box_a[0], box_b[0]))
		y_overlap = max(0, min(box_a[3], box_b[3]) - max(box_a[1], box_b[1]))
		intersection = x_overlap * y_overlap

		# Calculate union
		area_box_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
		area_box_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
		union = area_box_a + area_box_b - intersection

		if union == 0:
			return 0

		iou = intersection / union
		return iou

	def resize(self, image):

		if image.shape[0] > 600 or image.shape[1] > 600:
			ratio = min((300 / image.shape[0]), 
						(300 / image.shape[1]))

			shape_x = int(round(image.shape[0] * ratio))
			shape_y = int(round(image.shape[1] * ratio))

			image = scipy.misc.imresize(image, 
										(shape_x, shape_y))

			#print(image.shape)

		return image


	def predict_from_file(
			self,
			file_id):
		"""
		file_id, int, diffgram file id

		Assumes singular file for now
		"""

		if self.local is True:
			raise Exception("Not supported for local models yet.")

		request = {}
		request['file_list'] = [{'id' : file_id}]
		request['ai_name'] = self.name
		request['wait_for_inference'] = True


		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
			"/inference/add"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		inference = self.inference_from_response(data['inference'])
		return inference


	def local_setup(self):
		"""
		Intial setup for local prediction
		"""

		self.get_checkpoint_and_label_map()
		self.build()


	def get_checkpoint_and_label_map(self):
		"""

		Get download links
		Download checkpoint file for AI name

		"""
		request = {}
		request['ai_name'] = self.name

		endpoint = "/api/walrus/project/" + self.client.project_string_id + \
			"/brain/local_info"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()
		ai = data['ai']
		self.id = ai['id']


		# TODO continue to try and clarify label map crazinesss

		self.file_id_to_model_id = ai['label_dict']
		#print("Label map", self.file_id_to_model_id)

		self.model_id_to_file_id = {v: k for k, v in self.file_id_to_model_id.items()}
		self.file_id_to_name = {v: k for k, v in self.client.name_to_file_id.items()}


		self.build_model_id_to_name()
		
		# Data has url for models and label map
		# TODO clarify difference between local path and url to download model

		if self.use_temp_storage is True:
			self.model_path = self.temp + "/" + str(self.id) + ".pb"

		if self.use_temp_storage is False:
			self.model_path = self.local_model_storage_path

		self.url_model = ai['url_model']

		self.download_file(
			url = self.url_model,
			path = self.model_path)


	def build_model_id_to_name(self):
		"""Creates dictionary of COCO compatible categories keyed by category  id.
		Args:
		categories: a list of dicts, each of which has the following keys:
		'id': (required) an integer id uniquely identifying this category.
		'name': (required) string representing category name
		e.g., 'cat', 'dog', 'pizza'.
		Returns:
		category_index: a dict containing the same entries as categories, but  keyed
		by the 'id' field of each category.
		"""

		self.model_id_to_name = {}

		for file_id, label_name in self.file_id_to_name.items():

			model_id = self.file_id_to_model_id.get(str(file_id), None)

			if model_id:
				self.model_id_to_name[model_id] = {'name' : label_name}

		#print(self.model_id_to_name)



	def download_file(
			self,
			url,
			path
			):

		retry = 0
		while retry < 3:

			if url[0 : 4] != "http":
				return False

			response = requests.get(url, stream=True)

			if response.status_code != 200:
				retry += 1

			content_type = response.headers.get('content-type', None)

			with open(path, 'wb') as file:

				file.write(response.content)
			
			return True

		return False


	def check_status(
		  self):
		"""
		

		"""

		request = {}
		request['ai_name'] = self.name

		endpoint = "/api/walrus/v1/project/" + self.client.project_string_id + \
			"/brain/status"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()

		self.status = data['ai']['status']



	def clean(self):

		try:
			shutil.rmtree(self.temp)  # delete directory
		except OSError as exc:
			if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
				raise  # re-raise exception



	def build(self):
		"""
		Build graph for local prediction

		Assumes it has the checkpoint ready to go

		"""

		self.graph = tf.Graph()

		with self.graph.as_default():
			#with tf.device('/cpu:0'): # for local cpu testing
			graph_def = tf.GraphDef()

			with tf.gfile.GFile(self.model_path, 'rb') as fid:

				serialized_graph = fid.read()
				graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(graph_def, name='')

			self.sess = tf.Session(graph=self.graph)

		# TODO make this more flexible to work with different tensor types
		self.image_tensor = self.graph.get_tensor_by_name('encoded_image_string_tensor:0')
		self.detection_boxes = self.graph.get_tensor_by_name('detection_boxes:0')
		self.detection_scores = self.graph.get_tensor_by_name('detection_scores:0')
		self.detection_classes = self.graph.get_tensor_by_name('detection_classes:0')
		self.num_detections = self.graph.get_tensor_by_name('num_detections:0')

		self.build_complete = True

		return True




	def inference_from_local(
			self,):

		box_list = []
		score_list = []
		label_list = []

		for i in range(self.boxes.shape[0]):
			if self.scores[i] is None:
				pass            
			if self.scores[i] > self.min_score_thresh:

				#print("Detection")

				box_list.append(self.boxes[i].tolist())
				label_list.append(self.classes[i].tolist())
				score_list.append(self.scores[i].tolist()) 

		inference = Inference(
			method = self.method,
			id = None,
			status = None,
			box_list = box_list,
			score_list = score_list,
			label_list = label_list
			)

		return inference



	def visual(self,
			image = None
			):

		if image is None:
			image = self.image_backup

		# WIP

		#if self.sub_method == "default" or self.sub_method is None:

		#print("ran visual")

		vis_util.visualize_boxes_and_labels_on_image_array(
			image, 
			self.boxes, 
			self.classes, 
			self.scores,
			self.model_id_to_name,
			use_normalized_coordinates=True,
			line_thickness=3,
			min_score_thresh=self.min_score_thresh) 
			

		return image