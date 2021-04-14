# OPEN CORE - ADD
from shared.settings import settings
from shared.data_tools_core_gcp import DataToolsGCP
from shared.data_tools_core_s3 import DataToolsS3
from shared.data_tools_core_azure import DataToolsAzure


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class Data_tools(metaclass=Singleton):
	"""

	This assumes that 
	1) DIFFGRAM_STATIC_STORAGE_PROVIDER  is set as an env var  string options
	are 

	'gcp' 'aws'

	2) The credentials for the desired method are provided
	For GCP
		1)Current state is we have a
		string path to the service file env var name: SERVICE_ACCOUNT
		This is (we think) used in current app engine context

		K8S state:
		To be looked into. Also need this maybe. 3 options
		Env var that maybe is needed or better or default: 
			GOOGLE_APPLICATION_CREDENTIALS

		3 ways to load is
		1) JSON file using helm or something
		2) JSON file using instruction to hash it
		3) Mock the JSON like we do for connections thing

		Trade offs
			mounting volume on kubernetes (for 1 and 2)
			where as user manually parses file (for 3)
		
		2) Env var: CLOUD_STORAGE_BUCKET
		Pending merge with other branch.

	For AWS
		DIFFGRAM_AWS_ACCESS_KEY_ID
		DIFFGRAM_AWS_ACCESS_KEY_SECRET
		DIFFGRAM_S3_BUCKET_NAME
		ML__DIFFGRAM_S3_BUCKET_NAME   (Pending Rework)

	Main assumption here is that GCP and AWS don't conflict with each other
	eg so if using AWS don't have to fill GCP credentials.
	
	Assumption it's a low level thing and not changed.
	Assumption that we are somehow tracking this in Kubernetes sorta?
	"""

	def __init__(self):
		provider = settings.DIFFGRAM_STATIC_STORAGE_PROVIDER

		if not provider:
			raise ValueError("No DIFFGRAM_STATIC_STORAGE_PROVIDER env var set. valid values are [gcp, aws, azure]")

		if provider == 'gcp':
			self.data_tools = DataToolsGCP()
		elif provider == 'aws':
			self.data_tools = DataToolsS3()
		elif provider == 'azure':
			self.data_tools = DataToolsAzure()


data_tools = Data_tools().data_tools
