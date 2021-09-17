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

import oci
from oci.config import validate_config
from oci.object_storage import ObjectStorageClient

from google.cloud import storage
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob._models import BlobSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from google.oauth2 import service_account

# import file

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
        print(color + string + '\033[0m')

    @staticmethod
    def inputcolor(string, color = '\033[96m'):
        val = input(color + string + '\033[0m')
        return val


class DiffgramInstallTool:
    static_storage_provider = None
    bucket_name = None
    gcp_credentials_path = None
    s3_access_id = None
    s3_access_secret = None

    oci_user_ocid = None
    oci_fingerprint = None
    oci_key = None
    oci_tenancy_ocid = None
    oci_region = None

    azure_connection_string = None
    diffgram_version = None
    database_url = None
    local_database = None

    def set_static_storage_option(self, option_number):
        if option_number == 1:
            self.static_storage_provider = 'gcp'
        elif option_number == 2:
            self.static_storage_provider = 'aws'
        elif option_number == 3:
            self.static_storage_provider = 'azure'
        elif option_number == 4:
            self.static_storage_provider = 'oci'

    def set_gcp_credentials(self):
        is_valid = False
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
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Connection To Azure Account')
        except Exception as e:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Connection To Azure Account')
            bcolors.printcolor('Error Connecting to Azure: Please check you entered valid credentials.', bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            blob_client = client.get_blob_client(container = bucket_name, blob = test_file_path)
            my_content_settings = ContentSettings(content_type = 'text/plain')
            blob_client.upload_blob('This is a diffgram test file', content_settings = my_content_settings, overwrite=True)
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Write Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Write Permissions')
            bcolors.printcolor('Error Connecting to Azure: Please check you have write permissions on the Azure container.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
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
                content_disposition = 'attachment; filename=' + filename,
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
                    'Error when accessing presigned URL: Status({}). Error: {}'.format(resp.status_code, resp.text))

            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Read Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Read Permissions')
            bcolors.printcolor('Error Connecting to Azure: Please check you have read permissions on the Azure container.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
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
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Connection To GCP Account')
        except Exception as e:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Connection To GCP Account')
            bcolors.printcolor('Error Connecting to GCP: Please check you entered valid credentials.', bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            blob = bucket.blob(test_file_path)
            blob.upload_from_string('This is a diffgram test file', content_type = 'text/plain')
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Write Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Write Permissions')
            bcolors.printcolor('Error Connecting to GCP: Please check you have write permissions on the GCP bucket.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
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
                response_disposition = 'attachment; filename=' + filename
            )
            resp = requests.get(url_signed)
            if resp.status_code != 200:
                raise Exception(
                    'Error when accessing presigned URL: Status({}). Error: {}'.format(resp.status_code, resp.text))

            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Read Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Read Permissions')
            bcolors.printcolor('Error Connecting to GCP: Please check you have read permissions on the GCP bucket.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        bcolors.printcolor('Connection to GCP Successful!', bcolors.OKGREEN)
        return True

    def validate_oci_connection(self):

        test_file_path = 'diffgram_test_file.txt'
        client = None
        bcolors.printcolor('Testing Connection...', bcolors.OKBLUE)
        bucket_name = self.bucket_name
        # config = {
        #             "user":self.oci_user_ocid,
        #             "fingerprint":self.oci_fingerprint,
        #             "key_file":self.oci_key,
        #             "tenancy":self.oci_tenancy_ocid,
        #             "region":self.oci_region
        #         }
        config = oci.config.from_file()

        validate_config(config)
        
        bcolors.printcolor("Validate config OK",bcolors.OKGREEN)

        try:
            object_storage_client = ObjectStorageClient(config)
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Connection To OCI Account')
            bcolors.printcolor("Fetching Bucket Namespace",bcolors.OKBLUE)
            # get the namespace
            namespace = object_storage_client.get_namespace().data
            print(bcolors.OKGREEN + "Namespace:" + namespace)


        except Exception as e:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Connection To OCI Account')
            bcolors.printcolor('Error Connecting to OCI: Please check you entered valid credentials.', bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)

        try:
            Body = b'This is a diffgram test file'
            object_storage_client.put_object(namespace, bucket_name, test_file_path, Body)
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Write Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Write Permissions')
            bcolors.printcolor('Error Connecting to OCI: Please check you have write permissions on the OCI bucket.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)

        try:
            signed_url = object_storage_client.get_object(namespace, bucket_name, test_file_path)
            resp = signed_url.data
            if resp.status_code != 200:
                raise Exception(
                    'Error when accessing presigned URL: Status({}). Error: {}'.format(resp.status_code, resp.text))

            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Read Permissions')
        except:
            print(bcolors.WARNING + '[ERROR] ' + '\033[0m' + 'Read Permissions')
            bcolors.printcolor('Error Connecting to OCI: Please check you have read permissions on the OCI bucket.',
                               bcolors.WARNING)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        bcolors.printcolor('Connection to OCI Successful!', bcolors.OKGREEN)
        return True

    def validate_s3_connection(self):
        access_id = self.s3_access_id
        access_secret = self.s3_access_secret
        bucket_name = self.bucket_name
        test_file_path = 'diffgram_test_file.txt'
        client = None
        bcolors.printcolor('Testing Connection...', bcolors.OKBLUE)
        try:
            client = boto3.client('s3', aws_access_key_id = access_id, aws_secret_access_key = access_secret)
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Connection To S3 Account')
        except Exception as e:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Connection To S3 Account')
            bcolors.printcolor('Error Connecting to S3: Please check you entered valid credentials.', bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update credentials and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        try:
            client.put_object(Body = 'This is a diffgram test file',
                              Bucket = bucket_name,
                              Key = test_file_path,
                              ContentType = 'text/plain')
            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Write Permissions')
        except:
            print(bcolors.FAIL + '[ERROR] ' + '\033[0m' + 'Write Permissions')
            bcolors.printcolor('Error Connecting to S3: Please check you have write permissions on the S3 bucket.',
                               bcolors.FAIL)
            print('Details: {}'.format(traceback.format_exc()))
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
                    'Error when accessing presigned URL: Status({}). Error: {}'.format(resp.status_code, resp.text))

            print(bcolors.OKGREEN + '[OK] ' + '\033[0m' + 'Read Permissions')
        except:
            print(bcolors.WARNING + '[ERROR] ' + '\033[0m' + 'Read Permissions')
            bcolors.printcolor('Error Connecting to S3: Please check you have read permissions on the S3 bucket.',
                               bcolors.WARNING)
            print('Details: {}'.format(traceback.format_exc()))
            bcolors.printcolor('Please update permissions and try again', bcolors.OKBLUE)
            return False
        time.sleep(0.5)
        bcolors.printcolor('Connection to S3 Successful!', bcolors.OKGREEN)
        return True

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

    def set_oci_credentials(self):

        bcolors.printcolor("[*] Setup oci config.", bcolors.WARNING)
        bcolors.printcolor("In a new Terminal run: oci setup config ",bcolors.WARNING)
        # # Ask for user ocid
        # is_valid = False
        # while not is_valid:
        #     oci_user_ocid = bcolors.inputcolor('Please provide the OCI User OCID : ')
        #     if oci_user_ocid == '':
        #         print('Please a enter a valid value.')
        #         continue
        #     else:
        #         self.oci_user_ocid = oci_user_ocid
        #         is_valid = True
        
        # #Ask access key
        # is_valid = False
        # while not is_valid:
        #     oci_key = bcolors.inputcolor('Please provide the OCI Key (.pem file) : ')
        #     if oci_key == '':
        #         print('Please a enter a valid value.')
        #         continue
        #     else:
        #         self.oci_key = oci_key
        #         is_valid = True

        # #Ask for key fingerprint
        # is_valid = False
        # while not is_valid:
        #     oci_fingerprint = bcolors.inputcolor('Please provide the OCI key Fingerprint : ')
        #     if oci_fingerprint == '':
        #         print('Please a enter a valid value.')
        #         continue
        #     else:
        #         self.oci_fingerprint = oci_fingerprint
        #         is_valid = True
        
        # #Ask for tenancy ocid
        # is_valid = False
        # while not is_valid:
        #     oci_tenancy_ocid = bcolors.inputcolor('Please provide the OCI Tenancy OCID : ')
        #     if oci_tenancy_ocid == '':
        #         print('Please a enter a valid value.')
        #         continue
        #     else:
        #         self.oci_tenancy_ocid = oci_tenancy_ocid
        #         is_valid = True

        # # Ask for Home Region
        # is_valid = False
        # while not is_valid:
        #     oci_region = bcolors.inputcolor('Please provide the OCI Home Region : ')
        #     if oci_region == '':
        #         print('Please a enter a valid value.')
        #         continue
        #     else:
        #         self.oci_region = oci_region
        #         is_valid = True

        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the OCI BUCKET Name [Default is diffgram_buk]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram_buk'
        else:
            self.bucket_name = bucket_name

    def set_azure_credentials(self):
        # Ask For Access Key ID
        is_valid = False

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

        os_data = '{} {} {}'.format(os_name, system, release)
        return os_data

    def populate_env(self):
        env_file = ''
        bcolors.printcolor('Generating Environment Variables file...', bcolors.OKBLUE)
        if self.static_storage_provider == 'gcp':
            env_file = 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format(self.gcp_credentials_path)
            env_file += 'CLOUD_STORAGE_BUCKET={}\n'.format(self.bucket_name)
            env_file += 'ML__CLOUD_STORAGE_BUCKET={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
        elif self.static_storage_provider == 'aws':
            env_file = 'DIFFGRAM_AWS_ACCESS_KEY_ID={}\n'.format(self.s3_access_id)
            env_file += 'DIFFGRAM_AWS_ACCESS_KEY_SECRET={}\n'.format(self.s3_access_secret)
            env_file += 'DIFFGRAM_S3_BUCKET_NAME={}\n'.format(self.bucket_name)
            env_file += 'ML__DIFFGRAM_S3_BUCKET_NAME={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
            env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')
        elif self.static_storage_provider == 'azure':
            env_file = 'DIFFGRAM_AZURE_CONNECTION_STRING={}\n'.format(self.azure_connection_string)
            env_file += 'DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'ML__DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
            env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')
        
        elif self.static_storage_provider == 'oci':
            config = oci.config.from_file()
            data = [value for value in config.values()]
            env_file = 'DIFFGRAM_OCI_USER_OCID={}\n'.format(data[2])
            env_file += 'DIFFGRAM_OCI_FINGERPRINT={}\n'.format(data[3])
            env_file += 'DIFFGRAM_OCI_KEY={}\n'.format(data[4])
            env_file += 'DIFFGRAM_OCI_TENANCY_OCID={}\n'.format(data[5])
            env_file += 'DIFFGRAM_OCI_REGION={}\n'.format(data[6])
            env_file += 'DIFFGRAM_OCI_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'ML__DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
            env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')
        
        # elif self.static_storage_provider == 'oci':
        #     env_file = 'DIFFGRAM_OCI_USER_OCID={}\n'.format(self.oci_user_ocid)
        #     env_file += 'DIFFGRAM_OCI_FINGERPRINT={}\n'.format(self.oci_fingerprint)
        #     env_file += 'DIFFGRAM_OCI_KEY={}\n'.format(self.oci_key)
        #     env_file += 'DIFFGRAM_OCI_TENANCY_OCID={}\n'.format(self.oci_tenancy_ocid)
        #     env_file += 'DIFFGRAM_OCI_REGION={}\n'.format(self.region)
        #     env_file += 'DIFFGRAM_OCI_CONTAINER_NAME={}\n'.format(self.bucket_name)
        #     env_file += 'ML__DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
        #     env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
        #     env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
        #     env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')

        fernet_key = base64.urlsafe_b64encode(os.urandom(32))
        env_file += 'FERNET_KEY={}\n'.format(fernet_key)
        env_file += 'USER_PASSWORDS_SECRET={}\n'.format(create_random_string(10))
        env_file += 'INTER_SERVICE_SECRET={}\n'.format(create_random_string(10))
        env_file += 'SECRET_KEY={}\n'.format(create_random_string(18))
        env_file += 'WALRUS_SERVICE_URL_BASE={}\n'.format('http://walrus:8080/')

        env_file += 'DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE={}\n'.format(True)

        install_fingerprint = self.gen_install_finger_print()
        env_file += 'DIFFGRAM_INSTALL_FINGERPRINT={}\n'.format(install_fingerprint)
        env_file += 'DIFFGRAM_VERSION_TAG={}\n'.format(self.diffgram_version)
        env_file += 'DIFFGRAM_HOST_OS={}\n'.format(self.get_system_os())

        if self.local_database:
            env_file += 'POSTGRES_IMAGE={}\n'.format('postgres:12.5')
            env_file += 'DATABASE_URL={}\n'.format("postgresql+psycopg2://postgres:postgres@db/diffgram")
        else:
            env_file += 'POSTGRES_IMAGE={}\n'.format('tianon/true')
            env_file += 'DATABASE_URL={}\n'.format(self.database_url)

        text_file = open(".env", "w")
        text_file.write(env_file)
        text_file.close()
        bcolors.printcolor('✓ Environment file written to: {}'.format(os.path.abspath(text_file.name)), bcolors.OKGREEN)

    def launch_dockers(self):
        try:
            print('Launching Diffgram...')
            os.system('docker-compose up -d')
            print('✓ Diffgram Successfully Launched!')
            print('View the Web UI at: http://localhost:8085')
        except Exception as e:
            print('Error Launching diffgram {}'.format(str(e)))

    def set_diffgram_version(self):
        version = bcolors.inputcolor('Enter diffgram version: [Or Press Enter to Get The Latest Version]: ')
        if version == "":
            response = requests.get("https://api.github.com/repos/diffgram/diffgram/releases/latest")
            latest_release = response.json()['tag_name']
            self.diffgram_version = latest_release
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
                database_url = bcolors.inputcolor(
                    '\n\n >> Please enter the Remote Postgres Database URL\n    NOTE: The syntax for URL is: "postgresql+psycopg2://<db_username>:<db_pass>@/<db_name>?host=<db_host>": ',
                    bcolors.OKBLUE)

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
                    bcolors.printcolor('Error data: {}'.format(str(e)), bcolors.FAIL)
                    valid = False

    def install(self):
        self.print_logo()
        print('')
        print('')
        bcolors.printcolor('Welcome To the Diffgram Installer.', bcolors.OKGREEN)
        print('')
        print('')

        bcolors.printcolor('First We need to know what static storage provider you will use: ', bcolors.OKCYAN)
        print('1. Google Cloud Storage (GCP)')
        print('2. Amazon Web Services S3 (AWS S3)')
        print('3. Microsoft Azure Storage (Azure)')
        print('4. Oracle Cloud Storage (OCI)')

        option_valid = False
        while not option_valid:
            option = bcolors.inputcolor('Enter 1, 2, 3 or 4. Or write exit to quit the installation: ')

            if option.isnumeric() and int(option) in [1, 2, 3, 4]:
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
        
        elif self.static_storage_provider == 'oci':
            self.set_oci_credentials()
            if not self.validate_oci_connection():
                return

        self.set_diffgram_version()
        self.database_config()
        self.populate_env()
        self.launch_dockers()

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
