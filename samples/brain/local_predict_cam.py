import time
import tempfile
import os

import settings
from diffgram import Project

import cv2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from scipy.misc import imsave


"""

Example of predicting locally from webcam

-> using two different brains
-> displays results live using matplotlib
-> saves images to directory for review



"""


project = Project(
			client_id = settings.CLIENT_ID,
			client_secret = settings.CLIENT_SECRET,
			project_string_id = settings.PROJECT_STRING_ID,
			debug=False
			)

page_brain = project.get_model(
			name = "page",
			local = True)

graphs_brain = project.get_model(
			name = "graphs_three",
			local = True)


SAVE_IMAGES = True


# TODO optional to use temp directory
#temp = tempfile.mkdtemp()
#directory = temp + "/" + str(time.time()) + "/"

directory = str(time.time())

if not os.path.exists(directory):
    os.makedirs(directory)


cap = cv2.VideoCapture(0)
ax1 = plt.subplot(1,1,1)

image = ax1.imshow(grab_frame(cap))
ani = FuncAnimation(plt.gcf(), update, interval=100)

plt.show()


def grab_frame(cap):

	ret, frame = cap.read()

	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image_backup = np.copy(frame)

	# Expects encoded string tensor
	# So doing this to get around that
	path = temp + "/image.jpg"
	cv2.imwrite(path, frame)
	image = open(path, "rb")

	output_image = run_two_brains(
			image,
			image_backup,
			page_brain,
			graphs_brain)

	if SAVE_IMAGES is True:
		imsave(directory + "/" + str(time.time()) + ".jpg", output_image)

	return output_image


def run_two_brains(
	image,
	image_backup,
	alpha,
	bravo):

	image = image.read()

	page_inference = alpha.run(image)
	graphs_inference = bravo.run(image)

	# Optional, compute which boxes are near 
	# other ones for forming relations

	#alpha.nearest_iou( page_inference, graphs_inference)

	output_image = alpha.visual(image_backup)
	output_image = bravo.visual(output_image)

	return output_image


def update(i):
	image.set_data(grab_frame(cap))


