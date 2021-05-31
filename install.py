# -*- coding: utf-8 -*-
import os
import random
import string
import base64
import time

try:
    from sqlalchemy import create_engine
except Exception as e:
    raise(e)
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

    def set_gcp_credentials(self):
        is_valid = False
        # Ask For Service Account
        service_account_path = bcolors.inputcolor('Please provide the Full Path of your GCP service account JSON file: ')
        while not is_valid:
            try:
                if not service_account_path.endswith('.json'):
                    bcolors.printcolor('Path must be a JSON file', bcolors.WARNING)
                    is_valid = False
                    continue
                f = open(service_account_path)
                # Do something with the file
                self.gcp_credentials_path = service_account_path
                is_valid = True
            except IOError:
                bcolors.printcolor("Invalid path, make sure your are writing the full path to your GCP credentials JSON file", bcolors.FAIL)
            finally:
                f.close()
        # Ask for bucket name
        bucket_name = bcolors.inputcolor('Please provide the GCP Storage Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

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

        fernet_key = base64.urlsafe_b64encode(os.urandom(32))
        env_file += 'FERNET_KEY={}\n'.format(fernet_key)
        env_file += 'USER_PASSWORDS_SECRET={}\n'.format(create_random_string(10))
        env_file += 'INTER_SERVICE_SECRET={}\n'.format(create_random_string(10))
        env_file += 'SECRET_KEY={}\n'.format(create_random_string(18))
        env_file += 'WALRUS_SERVICE_URL_BASE={}\n'.format('http://walrus:8080/')
        env_file += 'DIFFGRAM_VERSION_TAG={}\n'.format(self.diffgram_version)

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
            self.diffgram_version = 'latest'
        else:
            self.diffgram_version = version

    def database_config(self):
        local_database = bcolors.inputcolor('Do you want to use the local database? Y/N [Press Enter to use Local DB]: ')
        local_database = local_database.lower()
        if local_database == 'y' or local_database == '':
            self.local_database = True
        else:
            self.local_database = False
            valid = False
            while not valid:
                database_url = bcolors.inputcolor(
                    '\n\n >> Please enter the Remote Postgres Database URL\n    NOTE: The syntax for URL is: "postgresql+psycopg2://<db_username>:<db_pass>@/<db_name>?host=<db_host>": ', bcolors.OKBLUE)

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
                    bcolors.printcolor('Connection test failed: Please check that your DB URL has the correct values and try again.', bcolors.FAIL)
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
        option_valid = False
        while not option_valid:
            option = bcolors.inputcolor('Enter 1, 2 or 3. Or write exit to quit the installation: ')

            if option.isnumeric() and int(option) in [1, 2, 3]:
                option_valid = True
                self.set_static_storage_option(int(option))
            elif option == 'exit':
                option_valid = True
                print('Thanks for using Diffgram :)')
                return
            else:
                print('Invalid option. Please enter either 1,2 or 3. Write exit to quit the installation process.')

        if self.static_storage_provider == 'gcp':
            self.set_gcp_credentials()
        elif self.static_storage_provider == 'aws':
            self.set_s3_credentials()
        elif self.static_storage_provider == 'azure':
            self.set_azure_credentials()

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
