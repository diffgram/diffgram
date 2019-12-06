

## What is Diffgram?:

Diffgram is all about Training Data:
Data that's ready to be used by AI systems.

It's created by combining raw data with human centered meaning. For example, combining an image with a box identifying an object. The encoded meaning can be relatively simple, for example a single bounding box, or complex, such as a time series video with a graph of attributes.

## Motivation

* Subject matter experts are the annotators and they need an easy way to do it.
* An increase in complexity in annotations and frequency of data change.
* Organization between data, people and teams on larger scale projects.

## What can I do with Diffgram SDK?

* Create batches of work (*Jobs*), including sending files
* Export annotations programmatically
* Create training data and work with files in a deep learning native format.

## Install

#### [Full Documentation](https://diffgram.readme.io/reference)


### Quickstart
`pip install diffgram`

On linux
`pip3 install diffgram`

1) [Get credentials from Diffgram.com](https://diffgram.readme.io/reference)
2) Download sample files from github
3) Config credentials


Example
```
from diffgram import Project

project = Project(project_string_id = "replace_with_project_string",
		  client_id = "replace_with_client_id",
		  client_secret = "replace_with_client_secret"	)
```


### [Import data](https://diffgram.readme.io/reference#input-from-url)


### Create a batch of work and send data to it

```
job = project.job.new()

for signed_url in signed_url_list:

	result = project.file.from_url(
		signed_url,
		job = job
	)

```
[Signed URL Guide](https://diffgram.readme.io/reference#example-signed-url)

### Importing from URL (ie cloud provider)

`result = project.file.from_url(url)`

(See our help article for signed URLS](https://intercom.help/diffgram/getting-started/uploading-media)


### [Importing existing instances](https://github.com/diffgram/diffgram/blob/master/sdk/samples/existing_instances/sample_image_with_existing_instances.py)

```

instance_bravo = {
		'type': 'box',
		'name': 'cat',
		'x_max': 128, 
		'x_min': 1,
		'y_min': 1,
		'y_max': 128
				}

# Combine into image packet

image_packet = {'instance_list' : [instance_alpha, instance_bravo],
		'media' : {
			'url' : "https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg",
			'type' : 'image'
			}
		}
	

result = project.file.from_packet(image_packet)

```

#### Importing a single local file:

`file = project.file.from_local(path)`

[Multiple file example](https://github.com/diffgram/diffgram/blob/master/sdk/samples/import/from_local_directory.py)


#### Beta
Note the API/SDK is in beta and is undergoing rapid improvment. There may be breaking changes.
Please see the [API docs](https://diffgram.readme.io/reference) for the latest canonical reference 
and be sure to upgrade to latest ie: `pip install diffgram --upgrade`. We will attempt to keep the SDK up to date with the API.

[Help articles for Diffgram.com](https://diffgram.readme.io/)  See below for some examples.

Requires Python >=3.5

The default install through pip will install dependencies
for local prediction (tensorflow opencv) as listed in `requirements.txt`.
The only requirement needed for majority of functions is `requests`. 
If you are looking for a minimal size install and already have requests use
the `--no-dependencies` flag ie `pip install diffgram --no-dependencies`



## Overall flow

The primary flow of using Diffgram is a cycle of 
importing data, training models, and updating those models, 
primarily by changing the data. Making use of the deep learning 
and collecting feedback to channel back to Diffgram is handled
in your system. [More on this here.](https://intercom.help/diffgram/getting-started/primary-flow-of-using-diffgram)

[![System diagram](https://downloads.intercomcdn.com/i/o/120647131/3d5f5b7df3b398ed60bff7ea/Activate+data%2C+active+models++Diffgram.png)](https://intercom.help/diffgram/getting-started/primary-flow-of-using-diffgram)

## Tutorials and walk throughs

[![System diagram](https://cdn-images-1.medium.com/max/2600/1*zts29hm2I1iSupZ5tdFevg.png)](https://medium.com/@anthony_sarkis/red-pepper-chef-from-new-training-data-to-deployed-system-in-a-few-lines-of-code-8d25b77fe447)

## [Red Pepper Chef - from new training data to deployed system in a few lines of code](https://medium.com/@anthony_sarkis/red-pepper-chef-from-new-training-data-to-deployed-system-in-a-few-lines-of-code-8d25b77fe447)

## [How to validate your model](https://medium.com/diffgram/how-to-validate-your-deep-learning-model-with-the-diffgram-sdk-tutorial-22234a9a35)

## [Fast Annotation Net](https://medium.com/diffgram/fast-annotation-net-a-framework-for-active-learning-in-2018-1c75d6b4af92)

---

### Code samples

[See samples folder](https://github.com/diffgram/diffgram/blob/master/sdk/samples)


## The project object
```
from diffgram import Project

project = Project(project_string_id = "replace_with_project_string",
		  client_id = "replace_with_client_id",
		  client_secret = "replace_with_client_secret"	)
```
The `project` represents the primary starting point.
The following examples assumes you have a project defined like this.

---

## Actions and Brains (Beta)

## [Brain](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain)

Benefits of using prediction through Diffgram brain

* Clean abstraction for different deep learning methods, local vs online prediction, and file types
* Designed for changing models and data. The same object you call .train() on can also call .predict()
* Ground up support for many models. See local_cam for one example.

And of course local prediction - your model is your model.

Note: We plan to support many deep learning methods in the future,
so while this is fairly heavily focused on object detection, the vast majority of
concepts carry over to semantic segmentation and other methods.

## [Train](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain/train.py)

```
brain = project.train.start(method="object_detection",
			    name="my_model")

brain.check_status()
```

---

## [Predict Online](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain/predict.py)

Predicting online requires no advanced setup and uses less local compute resources.

For predicting online there are 3 ways to send files

### Local file path
`inference = brain.predict_from_local(path)`

### URL, ie a remote cloud server
`inference = brain.predict_from_url(url)`

### From a diffgram file
`inference = brain.predict_from_file(file_id = 111546)`

---

## [Predict Local](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain/local_predict.py)

Predicting locally downloads the model weights, graph defintion, and relevant labels.
It will setup the model - warning this may use a significant amount of your local compute resources.
By default the model downloads to a temp directory, although you are welcome to download
and save the model to disk.

### [Local prediction, with local file](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain/local_predict.py)

Same as before, except we set the `local` flag to `True`
```
brain = project.get_model(
			name = None,
			local = True)
```
Then we can call

`inference = brain.predict_from_local(path)`


### [Local prediction, two models with visual](https://github.com/diffgram/diffgram/blob/master/sdk/samples/brain/local_predict_cam.py)

Get two models:

```
page_brain = project.get_model(
			name = "page_example_name",
			local = True)

graphs_brain = project.get_model(
			name = "graph_example_name",
			local = True)
```

This opens an image from a local path and runs both brains on same image.
We are only reading the image once, so you can stack as many networks
as you need here.

```

image = open(path, "rb")
image = image.read()

page_inference = page_brain.run(image)
graphs_inference = graphs_brain.run(image)

```

Optional, render a visual

```
output_image = page_brain.visual(image_backup)
output_image = graphs_brain.visual(output_image)
```

Imagine the "page" brain, most pages look the same, so it will need less data
and less retraining to reach an acceptable level of performance.
Then you can have a seperate network that gets retrained often to detect items of interest on the page (ie graphs).

![](https://storage.googleapis.com/diffgram-002/public/github/graph_example.png)
