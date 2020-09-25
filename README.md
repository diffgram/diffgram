
![](https://storage.googleapis.com/diffgram_public/marketing/logo/DiffgramLogoPNGrectangle.png "Logo")

[Diffgram.com](https://diffgram.com/)

### 91% of teams take > 3 weeks to create their first dataset. And months to get to Beta.

Here's why: The process of creating datasets gets blocked by default. As shown above, each clock represents a stage in which a user often must wait for other users, or other processes to finish before continuing.
Further, Teams create many sets. So after weeks of work the process repeats:

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/7d187f02-copy-of-process-ideal-to-create-one-set-stylized.svg "Process1")

This is because the needed abstractions (such as various Templates) only become known through an iterative process as shown above. 
Often many iterations are needed before shipping, and ongoing usage of the system requires further iterations to be effective.

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/c2a4971c-process-to-create-many-sets-styled-1.svg "Process2")

To manage all this, your team is likely doing a lot of "Extract Transform Load" operations. 
And managing sets with: "set_with_labels_good_one" and "good_one_really_this_time___v2"
Or writing a ton of one-off scripts.

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/cad17a4f-copy-of-the-most-expensive-copy-and-paster-in-the-world-just-tagline_1000000000000000000028.png "Diffgram Copy Paste")

And that's just for creating MVPs and beta products. 
When you get to production, most current setups look something like this.
Meaning even the best teams end up only shipping handfuls of models. Or investing heavily in recreating the wheel with infrastructure.

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/df711527-rubegoldberg-fb_10ta0fa00000000000001o.jpg)

## Introducing Diffgram

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/11119f7d-system-diagram-deploy-loop-example-development-cycle-benefits-new-vs-old-3.svg)

## Where Diffgram Integrates Into Your System

![](https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/2bfec8f4-overview-only-architecture-july-2020-1.svg)

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

## Install

#### [Full Documentation](https://diffgram.readme.io/docs)


### Quickstart
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

