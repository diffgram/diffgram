from diffgram.brain.inference import Inference


import tempfile

# TODO import these only if local prediction is needed
import cv2
import tensorflow as tf
import numpy as np
import requests
import scipy.misc
import base64

#import diffgram.utils.visualization_utils as vis_util


class Brain():

	def __init__(
			self, 
			client,
			name=None,
			id=None,
			local=False):
		"""
		client, project client object
		name, string, exact match for Diffgram AI name
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

		print(self.local)

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

		endpoint = "/api/v1/project/" + self.client.project_string_id + \
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
		but in one request to Diffgram (instead of two).

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
				
			endpoint = "/api/v1/project/" +  self.client.project_string_id \
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

	def run(self):

		if self.build_complete is False:
			return False

		with self.graph.as_default():
		
			# MUST HAVE compat.as_bytes for tf slim 
			# https://www.tensorflow.org/api_docs/python/tf/compat/as_bytes
			# https://stackoverflow.com/questions/46687348/decoding-tfrecord-with-tfslim

			self.image_to_run_expanded = tf.compat.as_bytes(self.image_to_run)

			self.image_to_run_expanded = np.expand_dims(self.image_to_run_expanded, axis=0)

			self.method = "object_detection"

			if self.sub_method == "default" or self.sub_method is None:

				self.run_object_detection()


	def resize(self, image):

		if image.shape[0] > 600 or image.shape[1] > 600:
			ratio = min((300 / image.shape[0]), 
						(300 / image.shape[1]))

			shape_x = int(round(image.shape[0] * ratio))
			shape_y = int(round(image.shape[1] * ratio))

			image = scipy.misc.imresize(image, 
										(shape_x, shape_y))

			print(image.shape)

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


		endpoint = "/api/project/" + self.client.project_string_id + \
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

		endpoint = "/api/project/" + self.client.project_string_id + \
			"/brain/local_info"

		response = self.client.session.post(
			self.client.host + endpoint, 
			json = request)

		self.client.handle_errors(response)

		data = response.json()
		ai = data['ai']
		self.id = ai['id']

		self.label_map = ai['label_dict']
		print(self.label_map)

		self.inverted_label_dict = {v: k for k, v in self.label_map.items()}

		self.category_index = self.inverted_label_dict
		
		# Data has url for models and label map

		# TODO clarify difference between local path and url to download model
		self.model_path = self.temp + "/" + str(self.id) + ".pb"
		self.url_model = ai['url_model']

		self.download_file(
			url = url_model,
			path = self.model_path)



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

			#print(response)

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

		endpoint = "/api/v1/project/" + self.client.project_string_id + \
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


	def inference_from_local(
			self,):

		box_list = []
		score_list = []
		label_list = []

		for i in range(self.boxes.shape[0]):
			if self.scores[i] is None:
				pass            
			if self.scores[i] > self.min_score_thresh:

				print("Detection")

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



	def capture_video():
		pass


	# WORK IN PROGRESS

	def grab_frame(self, cap):

		ret, frame = cap.read()

		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		self.image_backup = np.copy(frame)

		path = self.temp + "/image.jpg"

		# Really stupid work around 
		# Till figure out
		cv2.imwrite(path, frame)

		self.image_to_run = open(path, "rb")
		self.image_to_run = self.image_to_run.read()

		self.run()

		inference = self.inference_from_local()

		#self.visual()

		return self.image_backup


	def visual(self):

		# WIP

		#if self.sub_method == "default" or self.sub_method is None:

		#print("ran visual")

		vis_util.visualize_boxes_and_labels_on_image_array(
			self.image_backup, 
			self.boxes, 
			self.classes, 
			self.scores,
			self.category_index,
			use_normalized_coordinates=True,
			line_thickness=3,
			min_score_thresh=self.min_score_thresh) 
			
