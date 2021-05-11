

# Diffgram - Supervised Learning Data Platform

![](./github_assets/overview_diffgram_high_level.PNG)

Diffgram is annotation and training data software.

# What is Diffgram Exactly?
The domain is "Training Data".
It's one integrated system that handles everything in the new Training Data abstractions world.
It integrates with adjacent tools.

### Give me a Compass - What's the Stack look like?
Let's think of it like a loose analogy to LAMP, or MEAN stacks.
One example - use a pre-processing tool like Lightly, then do annotation in Diffgram, and model training with Determined AI. 
This is like a "LDD" stack: [lightly](https://github.com/lightly-ai/lightly) [diffgram](https://github.com/diffgram/diffgram) [determined-ai ](https://github.com/determined-ai).

You can use Diffgram with your choice of surrounding tools - the ones shown are examples and optional.
![](./github_assets/stack_example.PNG)

### Who are the end users?
* The largest group of end users is data annotators and subject matter experts.
* Data Scientists or similar sets up the Schema (labels and attributes), the dataset structure, etc.
* An admin or project manager sets up the human annotation pipelines.
* A software engineer sets up the overall system, data permissions, and maintaining a large deployment.

Note, to just get started a single user may play all roles.

### What is this a drop in replacement for?
Diffgram is a drop in replacement for *most* of the functions of the following systems: 
Labelbox, CVAT, SuperAnnotate, Label Studio (Heartex), V7 Labs (Darwin), BasicAI, SuperbAI, Kili-Technology, HastyAI, Dataloop, Keymakr.

If you see any missing features, bugs etc please report them ASAP to [diffgram/issues](https://github.com/diffgram/diffgram/issues).  See [Contribution Guide](https://diffgram.readme.io/docs/developer-contribution-guide) for more.

[More on Understanding Diffgram High Level](https://diffgram.readme.io/docs/help-im-new-what-is-diffgram-exactly)

# Quickstart

[Try Diffgram Online](https://diffgram.com/user/data_platform/new) (Hosted Service, No Setup.)

### Diffgram Dev Installer Quickstart
Requires Docker and Docker Compose
```
git clone https://github.com/diffgram/diffgram.git
cd diffgram
python install.py
# Follow the installer instruction and 
# After install:  View the Web UI at: http://localhost:8085
```
### Other Useful Links For Starting Out
- [Install Guide Compute Engine](https://medium.com/diffgram/tutorial-install-diffgram-in-google-compute-engine-134aae7d8a9b)
- [Updating Existing Installation](https://diffgram.readme.io/docs/updating-an-existing-installation)
- [Development Install Docs](https://diffgram.readme.io/docs/quickstart-installation-of-diffgram-open-core)
- [Production Install Docs](https://diffgram.readme.io/docs/open-installation-production)
- [Helm Chart for Kubernetes Clusters](https://github.com/diffgram/diffgram-helm)

# Benefits
1. Flexible deploy and many integrations - run Diffgram anywhere in the way you want.
2. Scale every aspect - from volume of data, to number of supervisors, to ML speed up approaches.
3. Fully featured - 'batteries included'.

# Docs
### [Docs](https://diffgram.readme.io/docs)
* [Getting Started Plan](https://diffgram.readme.io/docs/getting-started-plan)
* [Videos](https://www.youtube.com/channel/UC4ZVmvMA6oa3Lwaq6Si17pg/videos)
* [Cookbook (Advanced)](https://diffgram.readme.io/docs/cookbook)


# Support & Community
1. [Open an issue](https://github.com/diffgram/diffgram/issues) (Technical, bugs, etc)
2. [Chat on Discord](https://discord.gg/f5pf6UZHQT)
3. Forum (Coming Soon)

Security issues: Do not create a public issue. Email security@diffgram.com with the details.
[Docs](https://diffgram.readme.io/docs)

# Vision
1. Application: Support all popular media types for raw data; all popular schema, label, and attribute needs; and all annotation assist speed up approaches
2. Support all popular training data management and organizational needs
3. Integrate with all popular 3rd party applications and related offerings
4. Support modification of source code
5. Run on any hardware, any cloud, and anywhere

[Technical Direction](https://diffgram.readme.io/docs/direction)


# Features
[Overview Image and Video Annotation.](https://diffgram.com/software)

* [Segmentation](https://diffgram.com/segmentation)
* [Video Annotation](https://diffgram.com/video)
* [Versioning](https://diffgram.com/versioning)
* [Streaming](https://diffgram.com/streaming)
* [Security and Privacy](https://diffgram.com/secure)
* [Speed Up with AI Userscripts](https://diffgram.readme.io/docs/userscript-examples)
* Open Core (This Repo!)
* [Integrations](#integrations)

# Speed Ups & AI
Latest AI + More
* [Examples](https://diffgram.readme.io/docs/userscript-examples)
* [Userscripts Overview](https://diffgram.readme.io/docs/userscripts-overview)
![](./github_assets/userscript_diagram.png)


# Integrations

* [Diffgram Python SDK](https://github.com/diffgram/python-sdk)
* [Diffgram API](https://diffgram.readme.io/reference) Any language
* [AWS - Amazon Storage](https://diffgram.readme.io/docs/amazon-web-services-connection-requirements)
* [GCP Google Storage](https://diffgram.readme.io/docs/google-connection-requirements)
* Azure - (Select during install - not available as separate connection yet)
* [Scale AI](https://diffgram.readme.io/docs/scale-ai)
* [Datasaur](https://diffgram.readme.io/docs/datasaur-integration)
* [Labelbox](https://diffgram.readme.io/docs/labelbox-integration)
* Submit a pull request! We want your integration here too
 
![](./github_assets/levels_of_integrations.PNG)

Note for initial open core release Actions Hooks are not yet available. 
Please see Diffgram.com and use them there if needed.

# Contributing
We welcome contributions! Please see our [contributing documentation](https://diffgram.readme.io/docs/contributing-guide).

# Architecture & Design Docs
We plan to release more internal architecture docs over time. Please see the [general docs](https://diffgram.readme.io/docs) in the mean time.
