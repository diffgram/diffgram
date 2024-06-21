# -*- coding: utf-8 -*-
import os
import platform
import random
import string
import base64
import time
import boto3
import traceback
import hashlib
import uuid
import requests
import datetime

from google.cloud import storage
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob._models import BlobSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from google.oauth2 import service_account
from botocore.config import Config

try:
    from sqlalchemy import create_engine
except Exception as e:
    raise (e)
    print('Error: Some dependencies are missing on the Diffgram Installer.')
    print('Please try running: "pip3 install -r requirements.txt"')
    print('And try again.')
    exit(1)


def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + \
                                 string.digits) for x in range(length))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def printcolor(string, color):
        print(color + string + bcolors.ENDC)

    @staticmethod
    def inputcolor(string, color = '\033[96m'):
        val = input(color + string + bcolors.ENDC)
        return val


class DiffgramInstallTool:
    static_storage_provider = None
    bucket_name = None
    bucket_region = None
    gcp_credentials_path = None
    use_docker_minio:bool = True
    s3_endpoint_url = None
    s3_access_id = None
    s3_access_secret = None
    is_aws_signature_v4 = None
    azure_connection_string = None
    diffgram_version = None
    database_url = None
    local_database = None
    mailgun = None
    mailgun_key = None
    email_domain = None
    z_flag = None
    rabbit_port: int = 5672
    rabbit_host: str = 'localhost'
    rabbit_user_name: str = 'admin'
    rabbit_pass: str = 'admin'

    def set_static_storage_option(self, option_number):
        if option_number == 4:
            self.static_storage_provider = 'gcp'
        elif option_number == 2:
            self.static_storage_provider = 'aws'
        elif option_number == 3:
            self.static_storage_provider = 'azure'
        elif option_number == 1:
            self.static_storage_provider = 'minio'

    def set_gcp_credentials(self):
        is_valid = False
        self.use_docker_minio = False
        # Ask For Service Account
        while not is_valid:
            f = None
            service_account_path = bcolors.inputcolor(
                'Please provide the Full Path of your GCP service account JSON file: ')
            try:
                if not service_account_path.endswith('.json'):
                    bcolors.printcolor('ERROR: Path must be a JSON file', bcolors.WARNING)
                    is_valid = False
                    continue
                f = open(service_account_path)
                # Do something with the file
                self.gcp_credentials_path = service_account_path
                is_valid = True
            except IOError:
                bcolors.printcolor(
                    "Invalid path, make sure your are writing the full path to your GCP credentials JSON file",
                    bcolors.FAIL)
            finally:
                if f:
                    f.close()
        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the GCP Storage Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

    def validate_azure_connection(self):
        connection_string = self.azure_connection_string
        bucket_name = self.bucket_name
        test_file_path = 'diffgram_test_file.txt'
        client = None
        bcolors.printcolor('Testing Connection...', bcolors.OKBLUE)
        try:
            client = BlobServiceClient.from_connection_string(connection_string)
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Connection To Azure Account")
        except Exception as e:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Connection To Azure Account")
            bcolors.printcolor('Error Connecting to Azure: Please check you entered valid credentials.', bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            blob_client = client.get_blob_client(container = bucket_name, blob = test_file_path)
            my_content_settings = ContentSettings(content_type = 'text/plain')
            blob_client.upload_blob('This is a diffgram test file', content_settings = my_content_settings,
                                    overwrite = True)
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Write Permissions")
        except:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Write Permissions")
            bcolors.printcolor(
                'Error Connecting to Azure: Please check you have write permissions on the Azure container.',
                bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            shared_access_signature = BlobSharedAccessSignature(
                account_name = client.account_name,
                account_key = client.credential.account_key
            )
            expiration_offset = 40368000
            added_seconds = datetime.timedelta(0, expiration_offset)
            expiry_time = datetime.datetime.utcnow() + added_seconds
            filename = test_file_path.split("/")[-1]
            sas = shared_access_signature.generate_blob(
                container_name = bucket_name,
                blob_name = test_file_path,
                start = datetime.datetime.utcnow(),
                expiry = expiry_time,
                permission = BlobSasPermissions(read = True),
                content_disposition = f"attachment; filename={filename}",
            )
            sas_url = 'https://{}.blob.core.windows.net/{}/{}?{}'.format(
                client.account_name,
                bucket_name,
                test_file_path,
                sas
            )
            resp = requests.get(sas_url)
            if resp.status_code != 200:
                raise Exception(
                    f"Error when accessing presigned URL: Status({resp.status_code}). Error: {resp.text}")

            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Read Permissions")
        except:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Read Permissions")
            bcolors.printcolor(
                'Error Connecting to Azure: Please check you have read permissions on the Azure container.',
                bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        bcolors.printcolor('Connection to Azure Successful!', bcolors.OKGREEN)
        return True

    def validate_gcp_connection(self):
        account_path = self.gcp_credentials_path
        bucket_name = self.bucket_name
        test_file_path = 'diffgram_test_file.txt'
        client = None
        bucket = None
        bcolors.printcolor('Testing Connection...', bcolors.OKBLUE)
        try:
            file = open(account_path, mode = 'r')
            credentials = service_account.Credentials.from_service_account_file(account_path)
            client = storage.Client(credentials = credentials)
            bucket = client.get_bucket(bucket_name)
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Connection To GCP Account")
        except Exception as e:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Connection To GCP Account")
            bcolors.printcolor('Error Connecting to GCP: Please check you entered valid credentials.', bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            blob = bucket.blob(test_file_path)
            blob.upload_from_string('This is a diffgram test file', content_type = 'text/plain')
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Write Permissions")
        except:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Write Permissions")
            bcolors.printcolor('Error Connecting to GCP: Please check you have write permissions on the GCP bucket.',
                               bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            expiration_offset = 40368000
            expiration_time = int(time.time() + expiration_offset)
            bucket.blob(test_file_path)

            filename = test_file_path.split("/")[-1]
            url_signed = blob.generate_signed_url(
                expiration = expiration_time,
                response_disposition = f"attachment; filename={filename}"
            )
            resp = requests.get(url_signed)
            if resp.status_code != 200:
                raise Exception(
                    f"Error when accessing presigned URL: Status({resp.status_code}). Error: {resp.text}")

            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Read Permissions")
        except:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Read Permissions")
            bcolors.printcolor('Error Connecting to GCP: Please check you have read permissions on the GCP bucket.',
                               bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        bcolors.printcolor('Connection to GCP Successful!', bcolors.OKGREEN)
        return True

    def validate_s3_connection(self):
        if not self.use_docker_minio or self.static_storage_provider == 'aws':
            endpoint_url = self.s3_endpoint_url
        else:
            endpoint_url = 'http://localhost:9000'
        access_id = self.s3_access_id
        access_secret = self.s3_access_secret
        bucket_name = self.bucket_name
        bucket_region = self.bucket_region
        is_aws_signature_v4  = self.is_aws_signature_v4
        test_file_path = 'diffgram_test_file.txt'
        client = None
        bcolors.printcolor('Testing Connection...', bcolors.OKBLUE)
        try:
            if is_aws_signature_v4:
                client = boto3.client('s3', config=Config(signature_version='s3v4'), endpoint_url=endpoint_url, 
                                      aws_access_key_id=access_id, aws_secret_access_key=access_secret, region_name=bucket_region)
            else:
                client = boto3.client('s3', endpoint_url=endpoint_url, aws_access_key_id=access_id, aws_secret_access_key=access_secret, region_name=bucket_region)
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Connection To Storage")
        except Exception as e:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Connection To Storage")
            bcolors.printcolor('Error Connecting to S3: Please check you entered valid credentials.', bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            client.put_object(Body = 'This is a diffgram test file',
                              Bucket = bucket_name,
                              Key = test_file_path,
                              ContentType = 'text/plain')
            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Write Permissions")
        except:
            print(f"{bcolors.FAIL}[ERROR] {bcolors.ENDC}Write Permissions")
            bcolors.printcolor('Error Connecting to storage bucket: Please check you have write permissions on the bucket.',
                               bcolors.FAIL)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            signed_url = client.generate_presigned_url('get_object',
                                                       Params = {'Bucket': bucket_name, 'Key': test_file_path},
                                                       ExpiresIn = 3600 * 24 * 6)
            resp = requests.get(signed_url)
            if resp.status_code != 200:
                raise Exception(
                    f"Error when accessing presigned URL: Status({resp.status_code}). Error: {resp.text}")

            print(f"{bcolors.OKGREEN}[OK] {bcolors.ENDC}Read Permissions")
        except:
            print(f"{bcolors.WARNING}[ERROR] {bcolors.ENDC}Read Permissions")
            bcolors.printcolor('Error Connecting to S3: Please check you have read permissions on the S3 bucket.',
                               bcolors.WARNING)
            print(f"Details: {traceback.format_exc()}")
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        if self.static_storage_provider == 'minion':
            bcolors.printcolor('Connection to MinIO Successful!', bcolors.OKGREEN)
        else:
            bcolors.printcolor('Connection to S3 Successful!', bcolors.OKGREEN)
        return True

    def set_minio_credentials(self):
        use_docker_minio = bcolors.inputcolor('Would you like to provide a custom MinIO host? Default will use docker Y/N?')
        if use_docker_minio.lower() != 'y':
            self.use_docker_minio = True
            self.s3_endpoint_url = 'http://minio:9000'
            self.s3_access_id = create_random_string(20)
            self.s3_access_secret = create_random_string(40)
        else:
            self.use_docker_minio = False
        # Ask For Endpoint Url
        if not self.use_docker_minio:
            is_valid = False
            while not is_valid:
                s3_endpoint_url = bcolors.inputcolor('Please provide the Minio Endpoint Url: ')
                if s3_endpoint_url == '':
                    bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                    continue
                else:
                    self.s3_endpoint_url = s3_endpoint_url
                    is_valid = True

        # Ask For Access Key ID
        if not self.use_docker_minio:
            is_valid = False
            while not is_valid:
                s3_access_id = bcolors.inputcolor('Please provide the Minio Access Key ID: ')
                if s3_access_id == '':
                    bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                    continue
                else:
                    self.s3_access_id = s3_access_id
                    is_valid = True

            # Ask For Access Key Secret
            is_valid = False

            while not is_valid:
                s3_access_secret = bcolors.inputcolor('Please provide the Minio Access Key Secret: ')
                if s3_access_secret == '':
                    bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                    continue
                else:
                    self.s3_access_secret = s3_access_secret
                    is_valid = True

        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the Minio S3 Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

        # Ask for bucket region
        if not self.use_docker_minio:
            is_valid = False
            while not is_valid:
                bucket_region = bcolors.inputcolor('Please provide the Minio S3 Bucket Region: ')
                if bucket_region == '':
                    bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                    continue
                else:
                    self.bucket_region = bucket_region
                    is_valid = True

    def set_s3_credentials(self):

        # Ask For Access Key ID
        is_valid = False
        while not is_valid:
            s3_access_id = bcolors.inputcolor('Please provide the AWS Access Key ID: ')
            if s3_access_id == '':
                bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                continue
            else:
                self.s3_access_id = s3_access_id
                is_valid = True

        # Ask For Access Key Secret
        is_valid = False

        while not is_valid:
            s3_access_secret = bcolors.inputcolor('Please provide the AWS Access Key Secret: ')
            if s3_access_secret == '':
                bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                continue
            else:
                self.s3_access_secret = s3_access_secret
                is_valid = True

        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the AWS S3 Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

        # Ask for bucket region
        is_valid = False

        while not is_valid:
            bucket_region = bcolors.inputcolor('Please provide the AWS S3 Bucket Region: ')
            if bucket_region == '':
                bcolors.printcolor('Please a enter a valid value.', bcolors.WARNING)
                continue
            else:
                self.bucket_region = bucket_region
                is_valid = True

        # Ask for aws signature version 4
        is_aws_signature_v4 = bcolors.inputcolor('Use AWS Signature Version 4?[Y/n] ')
        if is_aws_signature_v4.lower() == 'y' or is_aws_signature_v4.lower() == 'yes':
            self.is_aws_signature_v4 = True
        else:
            self.is_aws_signature_v4 = False

    def set_azure_credentials(self):
        # Ask For Access Key ID
        is_valid = False
        self.use_docker_minio = False
        while not is_valid:
            azure_connection_string = bcolors.inputcolor('Please provide the Azure Connection String: ')
            if azure_connection_string == '':
                print('Please a enter a valid value.')
                continue
            else:
                self.azure_connection_string = azure_connection_string
                is_valid = True

        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the Azure Container Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

    def gen_install_finger_print(self):
        # Installation Fingeprint

        mac_addr = hex(uuid.getnode()).encode('utf-8')
        hash_object = hashlib.md5(mac_addr)
        fingerprint = hash_object.hexdigest()
        return fingerprint

    def get_system_os(self):
        os_name = os.name.lower()
        system = platform.system().lower()
        release = platform.release().lower()

        os_data = f"{os_name} {system} {release}"
        return os_data

    def populate_env(self):
        env_file = ''
        bcolors.printcolor('Generating Environment Variables file...', bcolors.OKBLUE)
        if self.static_storage_provider == 'gcp':
            env_file = f"GCP_SERVICE_ACCOUNT_FILE_PATH={self.gcp_credentials_path}\n"
            env_file += f"CLOUD_STORAGE_BUCKET={self.bucket_name}\n"
            env_file += f"ML__CLOUD_STORAGE_BUCKET={self.bucket_name}\n"
            env_file += f"DIFFGRAM_STATIC_STORAGE_PROVIDER={self.static_storage_provider}\n"
        elif self.static_storage_provider == 'aws':
            env_file = f"DIFFGRAM_AWS_ACCESS_KEY_ID={self.s3_access_id}\n"
            env_file += f"DIFFGRAM_AWS_ACCESS_KEY_SECRET={self.s3_access_secret}\n"
            env_file += f"DIFFGRAM_S3_BUCKET_NAME={self.bucket_name}\n"
            env_file += f"DIFFGRAM_S3_BUCKET_REGION={self.bucket_region}\n"
            env_file += f"IS_DIFFGRAM_S3_V4_SIGNATURE={self.is_aws_signature_v4}\n"
            env_file += f"ML__DIFFGRAM_S3_BUCKET_NAME={self.bucket_name}\n"
            env_file += f"DIFFGRAM_STATIC_STORAGE_PROVIDER={self.static_storage_provider}\n"
            env_file += "GCP_SERVICE_ACCOUNT_FILE_PATH=/dev/null\n"
        elif self.static_storage_provider == 'minio':
            env_file = f"DIFFGRAM_MINIO_ENDPOINT_URL={self.s3_endpoint_url}\n"
            env_file += f"DIFFGRAM_MINIO_ACCESS_KEY_ID={self.s3_access_id}\n"
            env_file += f"DIFFGRAM_MINIO_ACCESS_KEY_SECRET={self.s3_access_secret}\n"
            env_file += f"DIFFGRAM_S3_BUCKET_NAME={self.bucket_name}\n"
            env_file += f"DIFFGRAM_S3_BUCKET_REGION={self.bucket_region}\n"
            env_file += f"IS_DIFFGRAM_S3_V4_SIGNATURE={True}\n"
            env_file += f"ML__DIFFGRAM_S3_BUCKET_NAME={self.bucket_name}\n"
            env_file += f"DIFFGRAM_STATIC_STORAGE_PROVIDER={self.static_storage_provider}\n"
            env_file += "GCP_SERVICE_ACCOUNT_FILE_PATH=/dev/null\n"
        elif self.static_storage_provider == 'azure':
            env_file = f"DIFFGRAM_AZURE_CONNECTION_STRING={self.azure_connection_string}\n"
            env_file += f"DIFFGRAM_AZURE_CONTAINER_NAME={self.bucket_name}\n"
            env_file += f"ML__DIFFGRAM_AZURE_CONTAINER_NAME={self.bucket_name}\n"
            env_file += f"DIFFGRAM_STATIC_STORAGE_PROVIDER={self.static_storage_provider}\n"
            env_file += "GCP_SERVICE_ACCOUNT_FILE_PATH=/dev/null\n"

        fernet_key = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
        env_file += f"FERNET_KEY={fernet_key}\n"
        env_file += f"USER_PASSWORDS_SECRET={create_random_string(10)}\n"
        env_file += f"INTER_SERVICE_SECRET={create_random_string(10)}\n"
        env_file += f"SECRET_KEY={create_random_string(18)}\n"
        env_file += "WALRUS_SERVICE_URL_BASE=http://walrus:8082/\n"

        env_file += f"DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE={True}\n"

        install_fingerprint = self.gen_install_finger_print()
        env_file += f"DIFFGRAM_SYSTEM_MODE=sandbox\n"
        env_file += f"SERVICE_ACCOUNT_FULL_PATH=/gcp/gcp-service-account.json\n"
        env_file += f"GOOGLE_APPLICATION_CREDENTIALS=/gcp/gcp-service-account.json\n"
        env_file += f"PYTHONPATH=/gcp/gcp-service-account.json\n"
        env_file += f"DIFFGRAM_INSTALL_FINGERPRINT={install_fingerprint}\n"
        env_file += f"DIFFGRAM_VERSION_TAG={self.diffgram_version}\n"
        env_file += f"DIFFGRAM_HOST_OS={self.get_system_os()}\n"

        env_file += f"RABBITMQ_DEFAULT_USER={self.rabbit_username}\n"
        env_file += f"RABBITMQ_DEFAULT_PASS={self.rabbit_pass}\n"
        env_file += f"RABBITMQ_HOST={self.rabbit_host}\n"
        env_file += f"RABBITMQ_PORT={self.rabbit_port}\n"

        if self.local_database:
            env_file += "POSTGRES_IMAGE=postgres:16\n"
            env_file += "DATABASE_URL=postgresql+psycopg2://postgres:postgres@db/diffgram\n"
            env_file += "DATABASE_NAME=diffgram\n"
            env_file += "DATABASE_HOST=db\n"
            env_file += "DATABASE_NAME=diffgram\n"
            env_file += "DATABASE_USER=postgres\n"
            env_file += "DATABASE_PASS=postgres\n"
            env_file += "HEALTHCHECK_TEST_COMMAND=pg_isready\n"
            env_file += "HEALTHCHECK_TEST_ARG_0=-d\n"
            env_file += "HEALTHCHECK_TEST_ARG_1=db_prod\n"
        else:
            env_file += "POSTGRES_IMAGE=tianon/true\n"
            env_file += f"DATABASE_URL={self.database_url}\n"
            env_file += f"DATABASE_HOST={self.db_host}\n"
            env_file += f"DATABASE_NAME={self.db_name}\n"
            env_file += f"DATABASE_USER={self.db_username}\n"
            env_file += f"DATABASE_PASS={self.db_pass}\n"
            env_file += "HEALTHCHECK_TEST_COMMAND=echo\n"
            env_file += "HEALTHCHECK_TEST_ARG_0=remote_db_in_use\n"
            env_file += "HEALTHCHECK_TEST_ARG_1=none\n"

        if self.mailgun:
            env_file += f"MAILGUN_KEY={self.mailgun_key}\n"
            env_file += f"EMAIL_DOMAIN_NAME={self.email_domain}\n"

        if self.z_flag:
            env_file += "INTERNAL_POSTGRES_DIR=/var/lib/postgresql/data:Z\n"
        else:
            env_file += "INTERNAL_POSTGRES_DIR=/var/lib/postgresql/data\n"
        text_file = open(".env", "w")
        text_file.write(env_file)
        text_file.close()
        bcolors.printcolor(f"✓ Environment file written to: {os.path.abspath(text_file.name)}", bcolors.OKGREEN)

    def launch_dockers(self):
        try:
            print('Launching Diffgram...')
            if self.static_storage_provider == 'minio':
                os.system('docker compose --profile minio up -d')
            else:
                os.system('docker compose up -d')
            print('✓ Diffgram Successfully Launched!')
            print('View the Web UI at: http://localhost:8085')
        except Exception as e:
            print(f"Error Launching diffgram {str(e)}")

    def set_diffgram_version(self):
        version = bcolors.inputcolor('Enter diffgram version: [Or Press Enter to Get The Latest Version]: ')
        if version == "":
            self.diffgram_version = 'latest'
        else:
            self.diffgram_version = version

    def database_config(self):
        local_database = bcolors.inputcolor(
            'Do you want to use the local database? Y/N [Press Enter to use Local DB]: ')
        local_database = local_database.lower()
        if local_database == 'y' or local_database == '':
            self.local_database = True
        else:
            self.local_database = False
            valid = False
            while not valid:

                self.db_host = bcolors.inputcolor('Please provide the database host: ')
                self.db_name = bcolors.inputcolor('Please provide the database name: ')
                self.db_username = bcolors.inputcolor('Please provide the database username: ')
                self.db_pass = bcolors.inputcolor('Please provide the database password: ')

                # database_url = f"postgresql+psycopg2://{db_username}:{db_pass}@/{db_name}?host={db_host}"
                database_url = f"postgresql+psycopg2://{self.db_username}:{self.db_pass}@{self.db_host}/{self.db_name}"

                bcolors.printcolor('Testing DB Connection...', bcolors.WARNING)
                try:
                    # Testing connection
                    engine = create_engine(database_url)
                    conn = engine.connect()
                    conn.close()
                    valid = True
                    self.database_url = database_url
                    bcolors.printcolor('✓ DB connection succesful!', bcolors.OKGREEN)
                    time.sleep(2)
                except Exception as e:
                    bcolors.printcolor(
                        'Connection test failed: Please check that your DB URL has the correct values and try again.',
                        bcolors.FAIL)
                    bcolors.printcolor(f"Error data: {str(e)}", bcolors.FAIL)
                    valid = False

        z_flag = bcolors.inputcolor(
            'Do Add Z Flag to Postgres Mount? (Use only when using SELinux distros or similar) Y/N [Press Enter to Skip]: ')
        z_flag = z_flag.lower()
        if z_flag == 'y':
            self.z_flag = True
        else:
            self.z_flag = False

    def mailgun_config(self):
        need_mailgun = bcolors.inputcolor(
            'Do you want to add Mailgun to Diffgram?[Y/n] ')
        if need_mailgun.lower() == 'y' or need_mailgun.lower() == 'yes':
            mailgun_key = bcolors.inputcolor('Please provide the Mailgun key: ')
            email_domain = bcolors.inputcolor('Please provide the email domain: ')
            self.mailgun = True
            self.mailgun_key = mailgun_key
            self.email_domain = email_domain
            return
        return

    def rabbit_config(self):
        config_rabbit = bcolors.inputcolor(
            'Do you want to set RabbitMQ Config? \n (default config: localhost:5672 => user - password will be "admin" - "admin"? [Y/n] ')
        if config_rabbit.lower() == 'y' or config_rabbit.lower() == 'yes':
            rabbit_username = bcolors.inputcolor('Please provide the RabbitMQ username: ')
            rabbit_password = bcolors.inputcolor('Please provide the RabbitMQ password: ')
            rabbit_host = bcolors.inputcolor('Please provide the RabbitMQ host (example: localhost): ')
            rabbit_port = bcolors.inputcolor('Please provide the RabbitMQ port (example: 5672): ')
            self.rabbit_username = rabbit_username
            self.rabbit_pass = rabbit_password
            self.rabbit_host = rabbit_host
            self.rabbit_port = rabbit_port
        else:
            self.rabbit_username = 'admin'
            self.rabbit_pass = 'admin'
            self.rabbit_host = 'rabbitmq'
            self.rabbit_port = 5672

    def install(self):
        self.print_logo()
        print('')
        print('')
        bcolors.printcolor('Welcome To the Diffgram Installer.', bcolors.OKGREEN)
        print('')
        print('')

        bcolors.printcolor('First We need to know what static storage provider you will use: ', bcolors.OKCYAN)

        print('1. Minio Local Storage [Default]')
        print('2. Amazon Web Services S3 (AWS S3)')
        print('3. Microsoft Azure Storage (Azure)')
        print('4. Google Cloud Storage (GCP)')
        option_valid = False
        while not option_valid:
            option = bcolors.inputcolor('Enter 1, 2, 3 or 4. Or write exit to quit the installation: ')
            if option is None or option == '':
                # Default to MinIO
                option = 1
                option_valid = True
                self.set_static_storage_option(option)
            elif option.isnumeric() and int(option) in [1, 2, 3, 4]:
                option_valid = True
                self.set_static_storage_option(int(option))
            elif option == 'exit':
                option_valid = True
                print('Thanks for using Diffgram :)')
                return
            else:
                print('Invalid option. Please enter either 1, 2, 3 or 4. Write exit to quit the installation process.')

        if self.static_storage_provider == 'gcp':
            self.set_gcp_credentials()
            if not self.validate_gcp_connection():
                return
        elif self.static_storage_provider == 'aws':
            self.set_s3_credentials()
            if not self.validate_s3_connection():
                return
        elif self.static_storage_provider == 'azure':
            self.set_azure_credentials()
            if not self.validate_azure_connection():
                return
        elif self.static_storage_provider == 'minio':
            self.set_minio_credentials()
            if not self.use_docker_minio:
                self.set_minio_credentials()
                if not self.validate_s3_connection():
                    return
            
        self.set_diffgram_version()
        self.database_config()
        self.mailgun_config()
        self.rabbit_config()
        self.populate_env()
        self.launch_dockers()
        if self.use_docker_minio:
            if not self.validate_s3_connection():
                return

    def print_logo(self):
        print("""\
        ________  .__  _____  _____                            
        \______ \ |__|/ ____\/ ____\________________    _____  
            |    |  \|  \   __\\   __\/ ___\_  __ \__  \  /      \ 
            |    `   \  ||  |   |  | / /_/  >  | \// __ \|  Y Y   \

        /_______  /__||__|   |__| \___  /|__|  (____  /__|_|  /
                \/               /_____/            \/      \/
        """)

        print(""" 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&####@@@@@@@@@@@#////%#/%#@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#%///*##(///*######%##(///%*/*#*/##@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##/(#%#//*#//////////////////////%#@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@###/((/////////////////////////////*#%@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@##%%(*##///#////////////////////////////////*#%@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@#**/#**#////////////////////////////////////(#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%##%*#(///////#//##%#////(/////////////////////#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@#(***#*//(/////%,,,,%#%#(,#(///%##*///#///////%#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@#%**#/////////,,,,,,,,,,,,%#%%,,,##(#,#////##%@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@#%****%#//##//////*,,,,,,,,,,,,,,,,,#%,,,%##&@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%%***/#*////##////////*#%##%%#(/**,,,,,##@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@#%**/#*//////#///////##%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@#%*****##*(#///*///////(***%#######@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@##/*##/////////*%%#%(****#%//////#%#@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@##******%%////#//////////###%####//#%%#@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@#%****#(/////////%%*///*/%*%#@@##@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@##(*****##//#////////%#(/#//%*#%@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@&#*****%%///////////((##(**%/%#@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@#////***/#*/#/////////#//******%#@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@#@##*****##*////////////#********#&@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@&###%/*(##***#***%#//////*///////%********#%@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@&#**####****(%##(/#////////////*%*******%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@#%//##//*//*//**//////////#/*#******###@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@##*/////////////(#////////(%***%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@%#%////////////(#////////##*(##&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@&############(//////(#///////*%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#*////*/*%##%%###&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##//////*%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        
        """)


install_tool = DiffgramInstallTool()
install_tool.install()
