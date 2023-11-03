import os
import logging
from .env_adapter import EnvAdapter
import traceback

env_adapter = EnvAdapter()

DOCKER_CONTEXT = env_adapter.bool(os.getenv('DOCKER_CONTEXT', False))


def load_local_dev_env():
    if DOCKER_CONTEXT is True:
        return

    try:
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv('.env'))  # replace with your specific .env file
    except Exception as e:
        print(traceback.format_exc())

load_local_dev_env()

# Main Settings
DIFFGRAM_SYSTEM_MODE = os.environ.get('DIFFGRAM_SYSTEM_MODE', 'sandbox')
DIFFGRAM_STATIC_STORAGE_PROVIDER = os.environ.get('DIFFGRAM_STATIC_STORAGE_PROVIDER')
URL_BASE = os.getenv('URL_BASE', "http://localhost:8085/")
RUNNING_LOCALLY = env_adapter.bool(os.environ.get('RUNNING_LOCALLY', False))
NAME_EQUALS_MAIN = os.getenv('NAME_EQUALS_MAIN', False)  # Assumed to be running locally. Default when going to production is False

# Database Settings - Default to testing database
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/diffgram_testing')
UNIT_TESTING_DATABASE_URL = os.environ.get('UNIT_TESTING_DATABASE_URL')
DATABASE_CONNECTION_POOL_SIZE = int(os.getenv('DATABASE_CONNECTION_POOL_SIZE', 10))
DATABASE_IDLE_SESSION_TRANSACTION_TIMEOUT = int(os.getenv('DATABASE_IDLE_SESSION_TRANSACTION_TIMEOUT', 3600000)) # 1 Hour

# System Internal Secrets
USER_PASSWORDS_SECRET = os.environ.get('USER_PASSWORDS_SECRET', 'secret_for_users')
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
INTER_SERVICE_SECRET = os.environ.get('INTER_SERVICE_SECRET', 'default_inter_service_secret')
# Default key generated randomly. Please Do not use in production!!
FERNET_KEY = os.getenv('FERNET_KEY', 'NeL_RED6zZ1XF3XT7Yd1hzFPYyebrg6UdkECTOLHEdI=')


SANDBOX_LOGGER_TYPE = int(os.getenv('SANDBOX_LOGGER_TYPE', logging.INFO))


# AWS Settings
DIFFGRAM_S3_BUCKET_NAME = os.getenv('DIFFGRAM_S3_BUCKET_NAME')
DIFFGRAM_S3_BUCKET_REGION = os.getenv('DIFFGRAM_S3_BUCKET_REGION')
ML__DIFFGRAM_S3_BUCKET_NAME = os.getenv('ML__DIFFGRAM_S3_BUCKET_NAME')
DIFFGRAM_AWS_ACCESS_KEY_ID = os.environ.get('DIFFGRAM_AWS_ACCESS_KEY_ID')
DIFFGRAM_AWS_ACCESS_KEY_SECRET = os.environ.get('DIFFGRAM_AWS_ACCESS_KEY_SECRET')
IS_DIFFGRAM_S3_V4_SIGNATURE = env_adapter.bool(os.getenv('IS_DIFFGRAM_S3_V4_SIGNATURE', False))

# Minio Settings
DIFFGRAM_MINIO_ENDPOINT_URL = os.getenv('DIFFGRAM_MINIO_ENDPOINT_URL')  # Includes Port
DIFFGRAM_MINIO_ACCESS_KEY_ID = os.getenv('DIFFGRAM_MINIO_ACCESS_KEY_ID')
DIFFGRAM_MINIO_ACCESS_KEY_SECRET = os.getenv('DIFFGRAM_MINIO_ACCESS_KEY_SECRET')
DIFFGRAM_MINIO_DISABLED_SSL_VERIFY = env_adapter.bool(os.getenv('DIFFGRAM_MINIO_DISABLED_SSL_VERIFY', False))
    

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
ACTIONS_BASE_DIR = "actions/"
USER_IMAGES_BASE_DIR = "users/images/"
EXPORT_DIR = "export/"
SYSTEM_DATA_BASE_DIR = "diffgram-system/"

# Email Settings
DEFAULT_ENGINEERING_EMAIL = os.environ.get('DEFAULT_ENGINEERING_EMAIL', "")
EMAIL_VALIDATION = env_adapter.bool(os.environ.get('EMAIL_VALIDATION', False))
MAILGUN_KEY = os.getenv('MAILGUN_KEY')
EMAIL_DOMAIN_NAME = os.getenv('EMAIL_DOMAIN_NAME')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


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
EVENTHUB_URL = os.getenv('EVENTHUB_URL', 'https://app.diffgram.com/api/walrus/eventhub/new')
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
DOCKER_COMPOSE_CONTEXT = env_adapter.bool(os.getenv('DOCKER_COMPOSE_CONTEXT', False))  # True or False


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
ONLY_SUPER_ADMINS_CREATE_PROJECTS = env_adapter.bool(os.getenv('ONLY_SUPER_ADMINS_CREATE_PROJECTS', False))
DIFFGRAM_INSTALL_FINGERPRINT = os.getenv('DIFFGRAM_INSTALL_FINGERPRINT')
DIFFGRAM_VERSION_TAG = os.getenv('DIFFGRAM_VERSION_TAG')
DIFFGRAM_HOST_OS = os.getenv('DIFFGRAM_HOST_OS')
DIFFGRAM_SERVICE_NAME = os.getenv('DIFFGRAM_SERVICE_NAME')

EMAIL_REPLY_TO = os.getenv('EMAIL_REPLY_TO', 'support@diffgram.com')

# Plans Features
IS_OPEN_SOURCE = env_adapter.bool(os.getenv('IS_OPEN_SOURCE', True))
LARGE_API_CHUNK_SIZE = int(os.getenv('LARGE_API_CHUNK_SIZE', 5))

# System Info
RABBITMQ_DEFAULT_USER = os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_DEFAULT_PASS = os.getenv('RABBITMQ_DEFAULT_PASS')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')      # without port
USE_RABBIT_MQ = env_adapter.bool(os.getenv('USE_RABBIT_MQ', True))
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USE_SSL = env_adapter.bool(os.getenv('RABBITMQ_USE_SSL', False))


SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID = int(os.getenv('SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID', 5*3600*24))     # this should always be lower then new offset
SIGNED_URL_CACHE_NEW_OFFSET_SECONDS_VALID = int(os.getenv('SIGNED_URL_CACHE_NEW_OFFSET_SECONDS_VALID', 6*3600*24))

# OIDC Settings
USE_OAUTH2 = env_adapter.bool(os.getenv('USE_OAUTH2', False))
OAUTH2_PROVIDER_NAME = os.getenv('OAUTH2_PROVIDER_NAME', 'keycloak')
OAUTH2_PROVIDER_HOST = os.getenv('OAUTH2_PROVIDER_HOST', 'http://localhost:8099/auth/')
OAUTH2_PROVIDER_CLIENT_ID = os.getenv('OAUTH2_PROVIDER_CLIENT_ID', 'diffgram')
OAUTH2_PROVIDER_CLIENT_SECRET = os.getenv('OAUTH2_PROVIDER_CLIENT_SECRET')
OAUTH2_PROVIDER_PUBLIC_KEY = os.getenv('OAUTH2_PROVIDER_PUBLIC_KEY', 'diffgram_public_key')

if URL_BASE.endswith('/'):
    OAUTH2_DEFAULT_REDIRECT_URL = f'{URL_BASE}user/oauth2-login/'
    OAUTH2_DEFAULT_LOGOUT_URL = f'{URL_BASE}user/logout/'
    DEFAULT_LOGIN_URL = f'{URL_BASE}user/login/'
else:
    OAUTH2_DEFAULT_REDIRECT_URL = f'{URL_BASE}/user/oauth2-login/'
    OAUTH2_DEFAULT_LOGOUT_URL = f'{URL_BASE}/user/logout/'
    DEFAULT_LOGIN_URL = f'{URL_BASE}/user/login/'


DISABLE_SELF_REGISTRATION = env_adapter.bool(os.getenv('DISABLE_SELF_REGISTRATION', False))

# Cognito Settings
COGNITO_LOGIN_URL = os.getenv('COGNITO_LOGIN_URL')


# Keycloak Settings
KEY_CLOAK_MASTER_USER = os.getenv('KEY_CLOAK_MASTER_USER', 'admin')
KEY_CLOAK_MASTER_PASSWORD = os.getenv('KEY_CLOAK_MASTER_PASSWORD', 'admin')
KEY_CLOAK_DIFFGRAM_USER = os.getenv('KEY_CLOAK_DIFFGRAM_USER', 'diffgram')
KEY_CLOAK_DIFFGRAM_PASSWORD = os.getenv('KEY_CLOAK_DIFFGRAM_PASSWORD', 'diffgram')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'diffgram-realm')


# Minio Only Allow Expiry time is less than 7 days (value in seconds).
# https://github.com/minio/minio/blob/ca69e54cb6e4cff32b39cef6c7231c6d7ee6fca6/cmd/signature-v4-parser.go#L232
if DIFFGRAM_STATIC_STORAGE_PROVIDER == 'minio':
    SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID = min(SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID, 5*3600)
    SIGNED_URL_CACHE_NEW_OFFSET_SECONDS_VALID = min(SIGNED_URL_CACHE_NEW_OFFSET_SECONDS_VALID, 7*3600)

