import os
import logging
from .env_adapter import EnvAdapter

env_adapter = EnvAdapter()

# To read more about Environment Variables and settings in Diffgram visit:
# https://diffgram.com/docs/settings-environment-variables-and-secrets

# Secrets are always loaded from Environment Variables
# However, those can be set by another program, or loaded from another source
# Here is one example of loading them from a python file first before settings load.
try:
    from shared.settings.secrets import *
except Exception as e:
    print('Error loading secrets: ')
    print(e)


# Main Settings
DIFFGRAM_SYSTEM_MODE = os.environ.get('DIFFGRAM_SYSTEM_MODE', 'sandbox')
DIFFGRAM_STATIC_STORAGE_PROVIDER = os.environ.get('DIFFGRAM_STATIC_STORAGE_PROVIDER')
URL_BASE = os.getenv('URL_BASE', "http://127.0.0.1:8085/")
RUNNING_LOCALLY = env_adapter.bool(os.environ.get('RUNNING_LOCALLY', False))
NAME_EQUALS_MAIN = os.getenv('NAME_EQUALS_MAIN', False)  # Assumed to be running locally. Default when going to production is False

# Database Settings - Default to testing database
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/diffgram_testing')
UNIT_TESTING_DATABASE_URL = os.environ.get('UNIT_TESTING_DATABASE_URL')
DATABASE_CONNECTION_POOL_SIZE = int(os.getenv('DATABASE_CONNECTION_POOL_SIZE', 10))

# System Internal Secrets
USER_PASSWORDS_SECRET = os.environ.get('USER_PASSWORDS_SECRET', 'secret_for_users')
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
INTER_SERVICE_SECRET = os.environ.get('INTER_SERVICE_SECRET', 'default_inter_service_secret')
# Default key generated randomly. Please Do not use in production!!
FERNET_KEY = os.getenv('FERNET_KEY', 'NeL_RED6zZ1XF3XT7Yd1hzFPYyebrg6UdkECTOLHEdI=')


# Logger Settings - Defaults to INFO
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
SANDBOX_LOGGER_TYPE =  os.getenv('SANDBOX_LOGGER_TYPE', logging.INFO)


# AWS Settings
DIFFGRAM_S3_BUCKET_NAME = os.getenv('DIFFGRAM_S3_BUCKET_NAME')
DIFFGRAM_S3_BUCKET_REGION = os.getenv('DIFFGRAM_S3_BUCKET_REGION')
ML__DIFFGRAM_S3_BUCKET_NAME = os.getenv('ML__DIFFGRAM_S3_BUCKET_NAME')
DIFFGRAM_AWS_ACCESS_KEY_ID = os.environ.get('DIFFGRAM_AWS_ACCESS_KEY_ID')
DIFFGRAM_AWS_ACCESS_KEY_SECRET = os.environ.get('DIFFGRAM_AWS_ACCESS_KEY_SECRET')
IS_DIFFGRAM_S3_V4_SIGNATURE = env_adapter.bool(os.getenv('IS_DIFFGRAM_S3_V4_SIGNATURE', False))

# Minio Settings
DIFFGRAM_MINIO_ENDPOINT_URL = os.getenv('DIFFGRAM_MINIO_ENDPOINT_URL')
DIFFGRAM_MINIO_ACCESS_KEY_ID = os.getenv('DIFFGRAM_MINIO_ACCESS_KEY_ID')
DIFFGRAM_MINIO_ACCESS_KEY_SECRET = os.getenv('DIFFGRAM_MINIO_ACCESS_KEY_SECRET')
DIFFGRAM_MINIO_DISABLED_SSL_VERIFY = os.getenv('DIFFGRAM_MINIO_DISABLED_SSL_VERIFY', None)
DIFFGRAM_MINIO_DISABLED_SSL_VERIFY = False if DIFFGRAM_MINIO_DISABLED_SSL_VERIFY else None

# Azure Settings
DIFFGRAM_AZURE_CONTAINER_NAME = os.getenv('DIFFGRAM_AZURE_CONTAINER_NAME')
DIFFGRAM_AZURE_CONNECTION_STRING = os.getenv('DIFFGRAM_AZURE_CONNECTION_STRING')
ML__DIFFGRAM_AZURE_CONTAINER_NAME = os.getenv('ML__DIFFGRAM_AZURE_CONTAINER_NAME')

# Google Cloud Settings
GOOGLE_PROJECT_NAME = os.getenv('GOOGLE_PROJECT_NAME', "diffgram-sandbox")
CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET', "diffgram-sandbox")
ML__CLOUD_STORAGE_BUCKET = os.getenv('ML__CLOUD_STORAGE_BUCKET', "diffgram-sandbox")
SERVICE_ACCOUNT_FULL_PATH = os.getenv('SERVICE_ACCOUNT_FULL_PATH', "/enter/path/of/service/account")
REGION = "us-central1"

# For Cloud Storage Paths [Applies to all vendors]
PROJECT_IMAGES_BASE_DIR = "projects/images/"
PROJECT_VIDEOS_BASE_DIR = "projects/videos/"
PROJECT_RAW_IMPORT_BASE_DIR = "projects/raw_input/"
PROJECT_TEXT_FILES_BASE_DIR = "projects/text/"
PROJECT_PCD_FILES_BASE_DIR = "projects/pcd/"
PROJECT_GEOSPATIAL_FILES_BASE_DIR = "projects/geospatial/"
PROJECT_INSTANCES_IMAGES_BASE_DIR = "projects/instances/images/"
USER_IMAGES_BASE_DIR = "users/images/"
EXPORT_DIR = "export/"

# Email Settings
DEFAULT_ENGINEERING_EMAIL = os.environ.get('DEFAULT_ENGINEERING_EMAIL', "")
EMAIL_VALIDATION = env_adapter.bool(os.environ.get('EMAIL_VALIDATION', False))
MAILGUN_KEY = os.getenv('MAILGUN_KEY')
EMAIL_DOMAIN_NAME = os.getenv('EMAIL_DOMAIN_NAME')


# Walrus Settings
WALRUS_SERVICE_URL_BASE = os.getenv('WALRUS_SERVICE_URL_BASE', "http://127.0.0.1:8085/")
if not WALRUS_SERVICE_URL_BASE.endswith("/"):
    WALRUS_SERVICE_URL_BASE += "/"

PROCESS_MEDIA_NUM_FRAME_THREADS = int(os.getenv('PROCESS_MEDIA_NUM_FRAME_THREADS', 4))
PROCESS_MEDIA_NUM_VIDEO_THREADS = int(os.getenv('PROCESS_MEDIA_NUM_VIDEO_THREADS', 1))
PROCESS_MEDIA_REMOTE_QUEUE_ON = env_adapter.bool(os.environ.get('PROCESS_MEDIA_REMOTE_QUEUE_ON', True))
PROCESS_MEDIA_TRY_BLOCK_ON = env_adapter.bool(os.environ.get('PROCESS_MEDIA_TRY_BLOCK_ON', True))
PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY = env_adapter.bool(os.environ.get('PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY',
                                                                            False))  # default False because generally for production we don't want it

# Eventhub Settings
EVENTHUB_URL = os.getenv('EVENTHUB_URL', 'https://diffgram.com/api/walrus/eventhub/new')
ALLOW_EVENTHUB = env_adapter.bool(os.environ.get('ALLOW_EVENTHUB', False))

# Stripe
ALLOW_STRIPE_BILLING = env_adapter.bool(os.environ.get('ALLOW_STRIPE_BILLING', False))
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')


# Segment Key
_ANALYTICS_WRITE_KEY = os.environ.get('_ANALYTICS_WRITE_KEY')


# Other Misc Settings
SANDBOX_BYPASS_LOGIN = env_adapter.bool(os.getenv('SANDBOX_BYPASS_LOGIN', False))  # True or False
URL_SIGNED_REFRESH = int(os.getenv('URL_SIGNED_REFRESH', 1652572935))
ML_JOB_DIR = "job/"


# Security
MAX_PASSWORD_ATTEMPTS_BEFORE_LOCKOUT = 7


# Video / Image processing
DEFAULT_MAX_SIZE = 7680

# Diffgram Integrations
WEBHOOKS_URL_BASE = os.getenv('WEBHOOKS_URL_BASE', 'http://localhost:8085')


# Labelbox Integrations
LABEL_BOX_SECRET = os.getenv('LABELBOX_SECRET')  # Put a new generated secret here to auth callbacks (seperate from API keys)
LABEL_BOX_WEBHOOKS_URL = f'{WEBHOOKS_URL_BASE}/api/walrus/v1/webhooks/labelbox-webhook'

# Scale AI Integrations
SCALE_AI_WEBHOOKS_URL = f'{WEBHOOKS_URL_BASE}/api/walrus/v1/webhooks/scale-ai'

# Task Templates Threading Settings
TASK_TEMPLATE_THREAD_SLEEP_TIME_MIN = 30
TASK_TEMPLATE_THREAD_SLEEP_TIME_MAX = 200


# Sync Actions
SYNC_ACTIONS_THREAD_SLEEP_TIME_MIN = 3
SYNC_ACTIONS_THREAD_SLEEP_TIME_MAX = 120


# Actions Sync Thread
ACTION_THREAD_SLEEP_TIME_MIN = 60
ACTION_THREAD_SLEEP_TIME_MAX = 300

# Error Handling
DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE = env_adapter.bool(os.getenv('DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE', False))

# System Info
DIFFGRAM_INSTALL_FINGERPRINT = os.getenv('DIFFGRAM_INSTALL_FINGERPRINT')
DIFFGRAM_VERSION_TAG = os.getenv('DIFFGRAM_VERSION_TAG')
DIFFGRAM_HOST_OS = os.getenv('DIFFGRAM_HOST_OS')
DIFFGRAM_SERVICE_NAME = os.getenv('DIFFGRAM_SERVICE_NAME')

EMAIL_REPLY_TO = os.getenv('EMAIL_REPLY_TO', 'support@diffgram.com')

# Plans Features
IS_OPEN_SOURCE = env_adapter.bool(os.getenv('IS_OPEN_SOURCE', True))


SIGNED_URL_CACHE_MINIMUM_DAYS_VALID = int(os.getenv('SIGNED_URL_CACHE_MINIMUM_DAYS_VALID', 30 * 12))     # this should always be lower then new offset
SIGNED_URL_CACHE_NEW_OFFSET_DAYS_VALID = int(os.getenv('SIGNED_URL_CACHE_NEW_OFFSET_DAYS_VALID', 30 * 14))

print('DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE',DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE)

print("PROCESS_MEDIA_TRY_BLOCK_ON", PROCESS_MEDIA_TRY_BLOCK_ON)
print("PROCESS_MEDIA_REMOTE_QUEUE_ON", PROCESS_MEDIA_REMOTE_QUEUE_ON)
print("PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY", PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY)

print("DIFFGRAM_MINIO_ENDPOINT_URL", DIFFGRAM_MINIO_ENDPOINT_URL)
print("DIFFGRAM_MINIO_DISABLED_SSL_VERIFY", DIFFGRAM_MINIO_DISABLED_SSL_VERIFY)
print("DIFFGRAM_SYSTEM_MODE", "DIFFGRAM_SYSTEM_MODE ", DIFFGRAM_SYSTEM_MODE)
# Test everything loaded as expected.
print("DATABASE_URL", "DATABASE_URL ", bool(DATABASE_URL))


