
![](https://storage.googleapis.com/diffgram_public/marketing/logo/DiffgramLogoPNGrectangle.png "Logo")

[Diffgram.com](https://diffgram.com/)

# Your AI Data Annotation Platform

Quality Training Data for Enterprise - Data Labeling Software for Machine Learning

This Repo is the SDK. 

You can install the Diffgram Platform on your Kubernetes cluster or use Diffgram Online.

* [Security and Privacy](https://diffgram.com/secure)
* [Data Annotation Software](https://diffgram.com/software)
* [Image and Video Segmentation Software](https://diffgram.com/segmentation)
* [Video Annotation Software](https://diffgram.com/video)
* [Pro AI Data by Humans](https://diffgram.com/data_platform)

# On Your Kubernetes Cluster
Free Up to 3 Users. Enterprise licenses available see [pricing](https://diffgram.com/pricing)
![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/60f788a8-helm-kubernetes-logo_10fk09c000000000000028.png "Kubernetes")

### [Try Online Demo](https://diffgram.com/user/data_platform/new)
### [Kubernetes Full Install Guide](https://get.diffgram.com/kubernetes-install-guide-aws-amazon-elastic-kubernetes-service-k8s-helm-install-vpc-on-premise/)
### [Contact Us](https://diffgram.com/contact)

# Where Diffgram Integrates Into Your System

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/2bfec8f4-overview-only-architecture-july-2020-1.svg)

# Compare Diffgram
### [Diffgram vs Labelbox](https://get.diffgram.com/labelbox-vs-diffgram/data-tooling-annotation-labeling-tools-training-data/)
### [Diffgram vs Amazon Sagemaker Groundtruth (AWS)](https://get.diffgram.com/amazon-sagemaker-groundtruth-aws/sagemaker-vs-diffgram/compare-diffgram-sagemaker-ground-truth/)

## Diffgram as your Training Data Database

Diffgram is all about Training Data:
Data that's ready to be used by AI systems.

It's created by combining raw data with human centered meaning. For example, combining an image with a box identifying an object. The encoded meaning can be relatively simple, for example a single bounding box, or complex, such as a time series video with a graph of attributes.

[Tell me moar](https://diffgram.readme.io/docs/what-is-diffgram)

## Motivation

* An increase in complexity in annotations and frequency of data change.
* Organization between data, people and teams on larger scale projects.

[I need motivation](https://diffgram.readme.io/docs/why-choose-diffgram)

## Use Cases

* Create, Update, And Maintain Datasets
* Create processes for working with Deep Learning systems
* Compliance and threat actors
* Launch faster

[Use Cases Detail](https://diffgram.readme.io/docs/use-cases)

## SDK Install

#### [Full Documentation](https://diffgram.readme.io/docs)


### Quickstart Install SDK
`pip install diffgram`

On linux
`pip3 install diffgram`

[Credentials Guide](https://diffgram.readme.io/reference)
[Get Credentials from Diffgram.com](https://diffgram.com/) (or your Private Deploy Link)

Get a client project:
```
from diffgram import Project

project = Project(project_string_id = "replace_with_project_string",
		  client_id = "replace_with_client_id",
		  client_secret = "replace_with_client_secret"	)
```


## [Tasks Introduction](https://diffgram.readme.io/docs/tasks-introduction)

## [Import Introduction](https://diffgram.readme.io/docs/importing-your-data)

## [Updating Existing Instances](https://diffgram.readme.io/docs/importing-instances-walkthrough)

### [Pre-Label Example Video](https://youtu.be/55Hofp1H7yM)

## [Compatibility](https://diffgram.readme.io/docs/compatibility-will-diffgram-work-with-my-system)

# Interfaces

### [Diffgram (Image and Video)](https://diffgram.readme.io/docs/video-introduction)
### [Scale AI](https://diffgram.readme.io/docs/scale-ai)
### [Datasaur](https://diffgram.readme.io/docs/datasaur-integration)
### [Labelbox](https://diffgram.readme.io/docs/labelbox-integration)
### [Contact us to request an interface!](mailto:anthonysarkis+github@diffgram.com)

#### Beta
Note the API/SDK is in beta and is undergoing rapid improvement. There may be breaking changes.
Please see the [API docs](https://diffgram.readme.io/reference) for the latest canonical reference 
and be sure to upgrade to latest ie: `pip install diffgram --upgrade`. We will attempt to keep the SDK up to date with the API.

[Help articles for Diffgram.com](https://diffgram.readme.io/)  See below for some examples.

Requires Python >=3.5

The default install through pip will install dependencies
for local prediction (tensorflow opencv) as listed in `requirements.txt`.
The only requirement needed for majority of functions is `requests`. 
If you are looking for a minimal size install and already have requests use
the `--no-dependencies` flag ie `pip install diffgram --no-dependencies`

