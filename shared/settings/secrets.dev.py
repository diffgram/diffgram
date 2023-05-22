import os

os.environ[
    'DIFFGRAM_SYSTEM_MODE'] = DIFFGRAM_SYSTEM_MODE = "sandbox"  # "sandbox, production, staging, testing, testing_e2e
os.environ['DIFFGRAM_STATIC_STORAGE_PROVIDER'] = 'minio'
db_username = 'postgres'
db_pass = "postgres"
connector = "postgresql+psycopg2"
db_name = "diffgram"
db_host = "localhost"
if DIFFGRAM_SYSTEM_MODE == 'testing':
    db_name = 'diffgram_testing'
    os.environ[
        'UNIT_TESTING_DATABASE_URL'] = connector + "://" + db_username + ":" + db_pass + "@" + db_host + "/" + db_name
os.environ['DATABASE_URL'] = connector + "://" + db_username + ":" + db_pass + "@" + db_host + "/" + db_name
os.environ['EMAIL_VALIDATION'] = 'False'
os.environ['FERNET_KEY'] = '-ZAF_IzCwtJ3MQHXJNyGEWPTD46R-uPjlMVd_0fllVY='  # Test Key
os.environ['DATABASE_URL'] = connector + "://" + db_username + ":" + db_pass + "@" + db_host + "/" + db_name
os.environ['EMAIL_VALIDATION'] = 'False'
os.environ['USER_PASSWORDS_SECRET'] = 'secret'
os.environ['DB_SECRET'] = 'secret'
os.environ['SECRET_KEY'] = 'secret'

os.environ['WALRUS_SERVICE_URL_BASE'] = "http://127.0.0.1:8085/"
# MinIO / S3 Credentials
# os.environ['DIFFGRAM_AWS_ACCESS_KEY_ID'] = 'key'
# os.environ['DIFFGRAM_AWS_ACCESS_KEY_SECRET'] = 'secret'
os.environ['IS_DIFFGRAM_S3_V4_SIGNATURE'] = 'False'
os.environ['DIFFGRAM_S3_BUCKET_NAME'] = 'diffgram-storage'
os.environ['DIFFGRAM_S3_BUCKET_REGION'] = 'us-east-1'
os.environ['DIFFGRAM_MINIO_ENDPOINT_URL'] = 'http://localhost:9000'
os.environ['DIFFGRAM_MINIO_ACCESS_KEY_ID'] = 'mykeyi11vgy6rps3gimz18hd1'
os.environ['DIFFGRAM_MINIO_ACCESS_KEY_SECRET'] = 'mysecretvavkmgcooefsy0ff5aujj6965d4pvnrtrw0z23nr'
os.environ['DIFFGRAM_MINIO_DISABLED_SSL_VERIFY'] = 'True'
os.environ['ML__DIFFGRAM_S3_BUCKET_NAME'] = 'diffgram-storage'


os.environ['PROCESS_MEDIA_REMOTE_QUEUE_ON'] = 'True'
os.environ['PROCESS_MEDIA_TRY_BLOCK_ON'] = 'False'
os.environ['PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY'] = 'True'
os.environ['DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE'] = 'True'

os.environ['EMAIL_VALIDATION'] = "False"
os.environ['_ANALYTICS_WRITE_KEY'] = "123"
os.environ['ALLOW_EVENTHUB'] = 'True'
os.environ['EVENTHUB_URL'] = 'http://localhost:8085/api/walrus/eventhub/new'
os.environ['INTER_SERVICE_SECRET'] = "82727123123123kjashdkasjhsdas******aw"

os.environ['DIFFGRAM_HOST_OS'] = 'dev'
os.environ['PROCESS_MEDIA_NUM_FRAME_THREADS'] = '16'
os.environ['ALLOW_STRIPE_BILLING'] = 'True'
os.environ['DATABASE_CONNECTION_POOL_SIZE'] = '20'

os.environ['RABBITMQ_DEFAULT_USER'] = 'admin'
os.environ['RABBITMQ_DEFAULT_PASS'] = 'admin'
os.environ['RABBITMQ_HOST'] = 'localhost'
os.environ['RABBITMQ_PORT'] = '5672'
os.environ['RABBITMQ_USE_SSL'] = 'False'
os.environ['DIFFGRAM_INSTALL_FINGERPRINT'] = 'dev_pablo'

# General Oauth2 Settings
os.environ['USE_OAUTH2'] = 'False'