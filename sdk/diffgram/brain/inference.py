from diffgram.brain.instance import Instance


class Inference():
	"""
	Information from predictions
	"""


	def __init__(
		self,
		method = None,
		id = None,
		status = None,
		box_list = None,
		score_list = None,
		label_list = None):
		

		self.method = method
		self.box_list = box_list
		self.score_list = score_list
		self.label_list = label_list

		self.instance_list = []
		self.id = id
		self.status = status

		if self.method == "object_detection":
			self.object_detection_to_instances()

	
	def object_detection_to_instances(self):
		"""
		Converts list of predictions into Instance() objects
		"""

		for i, location in enumerate(self.box_list):

			instance = Instance(
				location = location,
				score = self.score_list[i],
				label = self.label_list[i]
				)

			self.instance_list.append(instance)






		



